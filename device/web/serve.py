import BaseHTTPServer
import json
import sqlite3
import traceback

PORT = 8080

class HttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    # override to avoid sending the 'Server' header
    def send_header(self, keyword, value):
        if not keyword == 'Server':
            BaseHTTPServer.BaseHTTPRequestHandler.send_header(self,keyword,value)

    def setDefaultHeaders(self):
        self.send_response(200)
        self.send_header("Content-type", "application/text")
        self.end_headers()
        
    def doRequest(self):
        self.setDefaultHeaders()
        self.REQUEST_MAPPING[self.command][self.path](self)
        self.wfile.flush()

    def do_POST(self):
        self.doRequest()

    def do_GET(self):
        self.doRequest()

    def ping(self):
        self.wfile.write(DEVICE_ID)

    def count(self):
        try:
            cursor = connection.cursor()
            cursor.execute("select count(*) from measurement where ifnull(status,'0') in ('0','2')")     
            record = cursor.fetchone()
            if record is None:
                raise Exception("No record retrieved when counting the measurements")
            if(len(record) == 0):
                raise Exception("Emtpy record retrieved when counting the measurements")
            self.wfile.write(record[0])
        except Exception as exc:
            print self.date_time_string()+" - An error occurred retrieving the number of measurements..."
            traceback.print_exc()            

    def send_measurements(self):
        content_len = int(self.headers.getheader('content-length', 0))
        body = json.loads(self.rfile.read(content_len))

        try:
            cursor = connection.cursor()

            limit_by_type = 'type' in body

            if limit_by_type:
                params=(body['type'])
            else:
                params=()

            update_initial_status_query = "update measurement set status='2' where trim(status) is null"
            if limit_by_type:
                update_initial_status_query += " and type=?"
            cursor.execute(update_initial_status_query,params)

            connection.commit()

            select_query = "select type||'#'||timing||'#'||value||'$' from measurement where status='2'"
            if limit_by_type:
                select_query += " and type=?"
            for measurement in cursor.execute(select_query,params):
                self.wfile.write(measurement[0])
            self.wfile.flush()

            update_final_status_query = "update measurement set status='5' where status='2'"
            if limit_by_type:
                update_final_status_query += " and type=?"
            cursor.execute(update_final_status_query,params)

            connection.commit()

        except Exception as exc:
            # this means that if an exception occurs somewhere during the updating/sending, then the measurements will be re-sent on next request.
            print self.date_time_string()+" - An error occurred sending the measurements..."
            traceback.print_exc()
            connection.rollback()        

    REQUEST_MAPPING = {
        'GET': {
            '/ping': ping,
            '/count': count
        },
        'POST': {
            '/': send_measurements
        }
    }

def get_device_id():
    # Extract serial from cpuinfo file
    cpuserial = "0000000000000000"
    try:
        f = open('/proc/cpuinfo','r')
        for line in f:
            if line[0:6]=='Serial':
                cpuserial = line[10:26]
        f.close()
    except:
        cpuserial = "ERROR000000000"

    return cpuserial

DEVICE_ID = get_device_id()

httpd = BaseHTTPServer.HTTPServer(("", PORT), HttpHandler)

print("Serving "+":".join(map(str,httpd.server_address))+" for device: "+DEVICE_ID)

try:
    connection = sqlite3.connect("../sqlite/measurements.db")
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    print "Exiting..."
    connection.close()
    httpd.socket.close()
    httpd.shutdown()
