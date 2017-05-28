""" Serve measurements via HTTP reading from sqlite database
"""

import json
import logging
import signal
import sqlite3
import BaseHTTPServer
import paho.mqtt.client as mqtt
from device_info import get_device_id
from constants import LOGGING_FORMAT, LOGGING_LEVEL, \
                      WEB_SERVER_PORT, \
                      SQLITE_DATABASE, TABLE_MEASUREMENTS, TABLE_PROPERTIES, \
                      MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE, MQTT_TOPIC_PROPERTIES

logging.basicConfig(format=LOGGING_FORMAT, level=LOGGING_LEVEL)
LOGGER = logging.getLogger('web_server')

class HttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """ Handler for HTTP. Exposes services defined in the REQUEST_MAPPING.
    """

    # override to avoid sending the 'Server' header
    def send_header(self, keyword, value):
        if not keyword == 'Server':
            BaseHTTPServer.BaseHTTPRequestHandler.send_header(self, keyword, value)

    # override because own logging implemented
    def log_message(self, format, *args):
        pass

    def _set_default_headers(self, response_code=200, content_type="application/text"):
        self.send_response(response_code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def _write_body(self, body):
        self.wfile.write(body)

    def _do_request(self):
        LOGGER.info("Handling request for client %s: %s %s", \
                               self.client_address[0], \
                               self.command, \
                               self.path)
        configuration = self.REQUEST_MAPPING[self.command][self.path]
        try:
            content_type = configuration['content_type']
            response_code = 200
            body = configuration['method'](self)
        except Exception:
            LOGGER.error("An error occurred creating body for method %s", \
                                           str(configuration['method']), \
                                           exc_info=True)
            content_type = "application/test"
            response_code = 500
            body = "Internal server error"

        LOGGER.debug("Creating response: HTTP/%s - %s - %s", \
                           response_code, \
                           content_type, \
                           body)
        self._set_default_headers(response_code=response_code, \
                                  content_type=content_type)
        self._write_body(body)

        self.wfile.flush()

    def do_POST(self):
        """ Dispatch HTTP POST requests
        """
        self._do_request()

    def do_GET(self):
        """ Dispatch HTTP POST requests
        """
        self._do_request()

    def ping(self):
        """ Ping response to see if the server is up. Responds the device id.
        """
        self.wfile.write(DEVICE_ID)

    def count(self):
        """ Return the number of measurements that have not yet been sent.
        """
        try:
            cursor = DATABASE_CONNECTION.cursor()
            query = "select count(*) from "+TABLE_MEASUREMENTS +\
                    " where ifnull(status,'0') in ('0','2')"
            LOGGER.debug("Executing query [%s]", query)
            cursor.execute(query)
            record = cursor.fetchone()
            if record is None:
                raise Exception("No record retrieved when counting the measurements")
            return record[0]
        except Exception:
            raise

    def retrieve_properties(self):
        """ Retrieve the properties from the database
        """
        try:
            cursor = DATABASE_CONNECTION.cursor()
            query = "select * from "+TABLE_PROPERTIES+" order by version desc"
            LOGGER.debug("Executing query [%s]", query)
            cursor.execute(query)
            record = cursor.fetchone()
            if record is None:
                raise Exception("No record retrieved when retrieving properties")
            result = {}
            for column in record.keys():
                if column == "version":
                    continue
                result[column] = record[column]
            return json.dumps(result)
        except Exception:
            raise

    def send_measurements(self):
        """ Send the measurements and update the database to indicate that they have been sent.
        """
        content_length = int(self.headers.getheader('content-length', 0))
        body = json.loads(self.rfile.read(content_length))
        LOGGER.debug("Received body: %s", body)

        try:
            cursor = DATABASE_CONNECTION.cursor()

            limit_by_type = 'type' in body

            if limit_by_type:
                params = (body['type'])
            else:
                params = ()

            update_initial_status_query = "update "+TABLE_MEASUREMENTS+ \
                              " set status='2' where trim(status) is null"
            if limit_by_type:
                update_initial_status_query += " and type=?"
            LOGGER.debug("Executing query [%s][%s]", update_initial_status_query, params)
            cursor.execute(update_initial_status_query, params)

            DATABASE_CONNECTION.commit()

            select_query = "select type||'#'||timing||'#'||value||'$' from "+ \
                                         TABLE_MEASUREMENTS+" where status='2'"
            if limit_by_type:
                select_query += " and type=?"
            result = ""
            LOGGER.debug("Executing query [%s][%s]", select_query, params)
            for measurement in cursor.execute(select_query, params):
                result += measurement[0]

            update_final_status_query = "update "+TABLE_MEASUREMENTS+ \
                                     " set status='5' where status='2'"
            if limit_by_type:
                update_final_status_query += " and type=?"
            LOGGER.debug("Executing query [%s][%s]", update_final_status_query, params)
            cursor.execute(update_final_status_query, params)

            DATABASE_CONNECTION.commit()
            return result

        except Exception:
            # this means that if an exception occurs somewhere during
            # the updating/sending, then the measurements will be re-sent
            # on next request.
            DATABASE_CONNECTION.rollback()
            raise

    def update_properties(self):
        """ Retrieve the properties from the database
        """
        content_length = int(self.headers.getheader('content-length', 0))
        body = json.loads(self.rfile.read(content_length))
        LOGGER.debug("Received body: [%s]", body)

        columns = []
        values = []

        for prop in body.keys():
            columns.append(prop)
            value = body[prop]
            values.append(value)
            MQTT_CLIENT.publish(MQTT_TOPIC_PROPERTIES+"/"+prop, value, qos=1)

        update_query = "insert into "+TABLE_PROPERTIES+" ("+(",".join(columns))+") "+ \
                        "values ("+",".join(['?' for _ in range(len(columns))])+")"
        try:
            cursor = DATABASE_CONNECTION.cursor()
            LOGGER.debug("Executing query [%s][%s]", update_query, values)
            cursor.execute(update_query, values)
            DATABASE_CONNECTION.commit()
            return "{}"
        except Exception:
            DATABASE_CONNECTION.rollback()
            raise

    REQUEST_MAPPING = {
        'GET': {
            '/ping': {
                'method': ping,
                'content_type': 'application/text'
            },
            '/measurements/count': {
                'method': count,
                'content_type': 'application/text'
            },
            '/properties': {
                'method': retrieve_properties,
                'content_type': 'application/json'
            }
        },
        'POST': {
            '/measurements': {
                'method': send_measurements,
                'content_type': 'application/text'
            },
            '/properties': {
                'method': update_properties,
                'content_type': 'application/json'
            }
        }
    }


if __name__ == "__main__":

    def _end_program(signum, frame):
        LOGGER.debug("Received termination signal %i", signum)
        _exit_program(0)

    def _exit_program(exit_code):
        if exit_code != 0:
            LOGGER.error("Exiting with error code %d", exit_code)
        else:
            LOGGER.info("Exiting normally")

        try:
            MQTT_CLIENT.loop_stop()
            MQTT_CLIENT.disconnect()
        except Exception:
            LOGGER.error('Exception occurred when trying to close mqtt client', exc__info=True)

        try:
            DATABASE_CONNECTION.close()
        except Exception:
            LOGGER.error('Exception occurred when trying to close database client', exc__info=True)

        try:
            SERVER.socket.close()
        except Exception:
            LOGGER.error('Exception occurred when trying to close server socket', exc__info=True)

        LOGGER.info("Done")
        exit(exit_code)

    LOGGER.info("Starting program")
    DEVICE_ID = get_device_id()

    try:
        LOGGER.debug("Creating mqtt client for host %s and port %s", MQTT_HOST, MQTT_PORT)
        MQTT_CLIENT = mqtt.Client()
        MQTT_CLIENT.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
        MQTT_CLIENT.loop_start()

        LOGGER.debug("Connecting to database %s", SQLITE_DATABASE)
        DATABASE_CONNECTION = sqlite3.connect(SQLITE_DATABASE)
        DATABASE_CONNECTION.row_factory = sqlite3.Row

        SERVER = BaseHTTPServer.HTTPServer(("", WEB_SERVER_PORT), HttpHandler)

        signal.signal(signal.SIGINT, _end_program)
        signal.signal(signal.SIGTERM, _end_program)

        LOGGER.info("Serving %s for device %s", \
                            ":".join(map(str, SERVER.server_address)), \
                            DEVICE_ID)

        SERVER.serve_forever()

    except Exception:
        LOGGER.error("Exception occurred", exc_info=True)
        _exit_program(1)
