"""Real local HTTP/SSE transport test; no GPU or external inference service."""
import importlib.util,json,threading,unittest
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer

spec=importlib.util.spec_from_file_location('measure_stream',Path(__file__).parents[1]/'labs/serving/measure_stream.py')
measure_stream=importlib.util.module_from_spec(spec);spec.loader.exec_module(measure_stream)
class Handler(BaseHTTPRequestHandler):
 def do_POST(self):
  self.rfile.read(int(self.headers['Content-Length']))
  if self.path.startswith('/error/'):
   self.send_error(503);return
  self.send_response(200);self.send_header('Content-Type','text/event-stream');self.end_headers()
  frames=[{'choices':[{'delta':{'role':'assistant','content':''}}]}, {'choices':[{'delta':{'content':'中文，多 token 合一'}}]}, {'choices':[],'usage':{'completion_tokens':7}}]
  for frame in frames:self.wfile.write(('data: '+json.dumps(frame)+'\n\n').encode())
  if not self.path.startswith('/truncated/'):self.wfile.write(b'data: [DONE]\n\n')
 def log_message(self,*args):pass

class StreamTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
  cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
  cls.url=f'http://127.0.0.1:{cls.server.server_port}'
 @classmethod
 def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
 def test_content_not_role_or_token(self):
  r=measure_stream.measure(self.url,'fixture','test',8)
  self.assertTrue(r['ok']);self.assertEqual(len(r['chunks']),1)
  self.assertEqual(r['usage']['completion_tokens'],7)
  self.assertLessEqual(r['first_content_seconds'],r['total_seconds'])
 def test_http_failure(self):self.assertFalse(measure_stream.measure(self.url+'/error','fixture','test',8)['ok'])
 def test_truncated_stream(self):
  r=measure_stream.measure(self.url+'/truncated','fixture','test',8)
  self.assertFalse(r['ok']);self.assertIn('[DONE]',r['error'])
if __name__=='__main__':unittest.main()
