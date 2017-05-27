""" Serve measurements via HTTP reading from sqlite database
"""

import signal
import json
import sqlite3
import traceback
import BaseHTTPServer
import paho.mqtt.client as mqtt
from device_info import get_device_id
from constants import WEB_SERVER_PORT, SQLITE_DATABASE, TABLE_MEASUREMENTS, TABLE_PROPERTIES, \
                      MQTT_HOST, MQTT_PORT, MQTT_TOPIC_PROPERTIES

class HttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """ Handler for HTTP. Exposes services defined in the REQUEST_MAPPING.
    """

    # override to avoid sending the 'Server' header
    def send_header(self, keyword, value):
        if not keyword == 'Server':
            BaseHTTPServer.BaseHTTPRequestHandler.send_header(self, keyword, value)

    def _set_default_headers(self, response_code=200, content_type="application/text"):
        self.send_response(response_code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def _do_request(self):
        self._set_default_headers()
        self.REQUEST_MAPPING[self.command][self.path](self)
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
            cursor.execute("select count(*) from "+TABLE_MEASUREMENTS+" where \
                                                 ifnull(status,'0') in ('0','2')")
            record = cursor.fetchone()
            if record is None:
                raise Exception("No record retrieved when counting the measurements")
            self.wfile.write(record[0])
        except Exception:
            print self.date_time_string()+" - An error occurred retrieving \
                                                   the number of measurements..."
            traceback.print_exc()

    def retrieve_properties(self):
        """ Retrieve the properties from the database
        """
        try:
            cursor = DATABASE_CONNECTION.cursor()
            cursor.execute("select * from "+TABLE_PROPERTIES+" \
                                 order by version desc")
            record = cursor.fetchone()
            if record is None:
                raise Exception("No record retrieved when retrieving properties")
            result = ""
            for column in record.keys():
                if column == "version":
                    continue
                result += column+":"+str(record[column])+"#"
            self.wfile.write(result)
        except Exception:
            print self.date_time_string()+" - An error occurred retrieving \
                                                   the properties..."
            traceback.print_exc()

    def send_measurements(self):
        """ Send the measurements and update the database to indicate that they have been sent.
        """
        content_len = int(self.headers.getheader('content-length', 0))
        body = json.loads(self.rfile.read(content_len))

        try:
            cursor = DATABASE_CONNECTION.cursor()

            limit_by_type = 'type' in body

            if limit_by_type:
                params = (body['type'])
            else:
                params = ()

            update_initial_status_query = "update "+TABLE_MEASUREMENTS+" set status='2' \
                                                     where trim(status) is null"
            if limit_by_type:
                update_initial_status_query += " and type=?"
            cursor.execute(update_initial_status_query, params)

            DATABASE_CONNECTION.commit()

            select_query = "select type||'#'||timing||'#'||value||'$' from "+TABLE_MEASUREMENTS+" \
                                                     where status='2'"
            if limit_by_type:
                select_query += " and type=?"
            for measurement in cursor.execute(select_query, params):
                self.wfile.write(measurement[0])
            self.wfile.flush()

            update_final_status_query = "update "+TABLE_MEASUREMENTS+" set status='5' \
                                                     where status='2'"
            if limit_by_type:
                update_final_status_query += " and type=?"
            cursor.execute(update_final_status_query, params)

            DATABASE_CONNECTION.commit()

        except Exception:
            # this means that if an exception occurs somewhere during
            # the updating/sending, then the measurements will be re-sent
            # on next request.
            print self.date_time_string()+" - An error occurred sending the measurements..."
            traceback.print_exc()
            DATABASE_CONNECTION.rollback()

    def update_properties(self):
        """ Retrieve the properties from the database
        """
        content_len = int(self.headers.getheader('content-length', 0))
        body = self.rfile.read(content_len)

        properties = body.split("#")

        columns = []
        values = []

        for prop in properties:
            if not prop:
                break
            name, value = prop.split(":")
            columns.append(name)
            values.append(value)
            MQTT_CLIENT.publish(MQTT_TOPIC_PROPERTIES+"/"+name, value, qos=1)

        update_query = "insert into "+TABLE_PROPERTIES+" ("+(",".join(columns))+") "+\
                        "values ("+",".join(['?' for _ in range(len(columns))])+")"
        try:
            cursor = DATABASE_CONNECTION.cursor()
            cursor.execute(update_query, values)
            DATABASE_CONNECTION.commit()
        except Exception:
            print self.date_time_string()+" - An error occurred updating \
                                                   the properties..."
            traceback.print_exc()
            DATABASE_CONNECTION.rollback()

    REQUEST_MAPPING = {
        'GET': {
            '/ping': ping,
            '/measurements/count': count,
            '/properties': retrieve_properties
        },
        'POST': {
            '/measurements': send_measurements,
            '/properties': update_properties
        }
    }


if __name__ == "__main__":

    def _end_program(signum, frame):
        _exit_program(0)

    def _exit_program(exit_code):
        print "Exiting... ("+str(exit_code)+")"
        MQTT_CLIENT.loop_stop()
        MQTT_CLIENT.disconnect()
        DATABASE_CONNECTION.close()
        SERVER.socket.close()
        exit(exit_code)

    DEVICE_ID = get_device_id()

    try:
        MQTT_CLIENT = mqtt.Client()
        MQTT_CLIENT.connect(MQTT_HOST, MQTT_PORT)
        MQTT_CLIENT.loop_start()

        DATABASE_CONNECTION = sqlite3.connect(SQLITE_DATABASE)
        DATABASE_CONNECTION.row_factory = sqlite3.Row

        SERVER = BaseHTTPServer.HTTPServer(("", WEB_SERVER_PORT), HttpHandler)

        print "Serving "+":".join(map(str, SERVER.server_address))+" for device: "+DEVICE_ID

        signal.signal(signal.SIGINT, _end_program)
        signal.signal(signal.SIGTERM, _end_program)

        SERVER.serve_forever()

    except Exception:
        traceback.print_exc()
        _exit_program(1)
