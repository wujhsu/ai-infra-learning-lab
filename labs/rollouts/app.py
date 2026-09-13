"""CPU-only controlled bad-version fixture. Not a model serving benchmark."""
import os,time
from http.server import BaseHTTPRequestHandler,HTTPServer
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path=='/health':status=200
  else:
   time.sleep(float(os.getenv('LATENCY_SECONDS','0')))
   status=500 if os.getenv('FAIL','false')=='true' else 200
  self.send_response(status);self.end_headers();self.wfile.write(str(status).encode())
HTTPServer(('0.0.0.0',int(os.getenv('PORT','8000'))),Handler).serve_forever()
