# python server.py  → http://localhost:8765/ （配信） /control.html （設定）。他のPCから使うなら HOST=0.0.0.0 python server.py
import json,os,queue
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
D=os.path.dirname(os.path.abspath(__file__));F=os.path.join(D,'state.json');cl=[];last=None
try: last=json.load(open(F,encoding='utf-8'))
except Exception: pass
class H(BaseHTTPRequestHandler):
  def log_message(s,*a):pass
  def out(s,code,body=b'',ct='text/plain'):
    s.send_response(code);s.send_header('Content-Type',ct);s.send_header('Cache-Control','no-store');s.send_header('Content-Length',str(len(body)));s.end_headers();s.wfile.write(body)
  def do_GET(s):
    u=s.path.split('?')[0]
    if u=='/events':
      s.send_response(200);s.send_header('Content-Type','text/event-stream');s.send_header('Cache-Control','no-cache');s.end_headers()
      q=queue.Queue();cl.append(q)
      try:
        s.wfile.write(b':ok\n\n');s.wfile.flush()
        while True:
          try: s.wfile.write(b'data: '+q.get(timeout=15)+b'\n\n')
          except queue.Empty: s.wfile.write(b':\n\n')
          s.wfile.flush()
      except Exception: pass
      finally: cl.remove(q)
      return
    if u=='/state': return s.out(200,json.dumps(last).encode(),'application/json')
    n={'/':'index.html','/index.html':'index.html','/control.html':'control.html'}.get(u)
    if n:
      for d in (D,os.getcwd()):
        f=os.path.join(d,n)
        if os.path.isfile(f): return s.out(200,open(f,'rb').read(),'text/html; charset=utf-8')
      return s.out(404,('%s が見つかりません。server.py と同じフォルダ（%s）に index.html と control.html を置いてください。'%(n,D)).encode('utf-8'),'text/plain; charset=utf-8')
    s.out(404)
  def do_POST(s):
    global last
    b=s.rfile.read(int(s.headers.get('Content-Length',0)))
    try:
      if json.loads(b).get('t')=='state':
        last=json.loads(b);open(F,'wb').write(b)
      for q in list(cl): q.put(b)
    except Exception: pass
    s.out(204)
for n in ('index.html','control.html'):
  if not os.path.isfile(os.path.join(D,n)) and not os.path.isfile(os.path.join(os.getcwd(),n)): print('【注意】%s が %s にありません。同じフォルダに置いてください'%(n,D))
print('配信 http://localhost:8765/   設定 http://localhost:8765/control.html')
ThreadingHTTPServer((os.environ.get('HOST','127.0.0.1'),8765),H).serve_forever()
