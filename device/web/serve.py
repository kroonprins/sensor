import BaseHTTPServer
import json
import sqlite3
import traceback

PORT = 8080

class HttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_POST(self):
        content_len = int(self.headers.getheader('content-length', 0))
        body = json.loads(self.rfile.read(content_len))

        self.send_response(200)
        self.send_header("Content-type", "application/text")
        self.end_headers()
 
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
            print "An error occurred..."
            traceback.print_exc()
            connection.rollback()
        

    # override to avoid sending the 'Server' header
    def send_header(self, keyword, value):
        if not keyword == 'Server':
            BaseHTTPServer.BaseHTTPRequestHandler.send_header(self,keyword,value)

#httpd = SocketServer.TCPServer(("", PORT), HttpHandler)
httpd = BaseHTTPServer.HTTPServer(("", PORT), HttpHandler)

print("Serving "+":".join(map(str,httpd.server_address)))

try:
    connection = sqlite3.connect("/home/pi/sqlite/test.db")
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    print "Exiting..."
    connection.close()
    httpd.socket.close()
    httpd.shutdown()
