import urllib.request,json,hashlib,sys,time
from pathlib import Path
Path('sources').mkdir(exist_ok=True)
for f in json.loads(Path(sys.argv[1]).read_text()):
 assert Path(f['name']).name==f['name'] and f['name'] not in ('.','..')
 assert f['azul_mirror_uri']=='s3://humancellatlas/file/'+f['sha256']+'.sha256'
 p=Path('sources')/f['name']
 if p.exists():
  assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'];continue
 u=f['azul_mirror_uri'].replace('s3://humancellatlas/','https://humancellatlas.s3.amazonaws.com/')
 h=hashlib.sha256();n=0;tmp=Path(str(p)+'.partial')
 with urllib.request.urlopen(u,timeout=45) as r,tmp.open('xb') as out:
  while b:=r.read(1048576):
   n+=len(b)
   if n>f['size']:raise ValueError('Excess bytes')
   out.write(b);h.update(b);time.sleep(.1)
 assert n==f['size'] and h.hexdigest()==f['sha256']
 tmp.rename(p);print(f['name'],n,'verified')
