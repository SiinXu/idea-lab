#!/usr/bin/env python3
"""Fetch <title> for every evidence URL in docs/d/*.json -> scripts/ev_titles.json (cache; reuses existing titles)."""
import json,glob,re,html,os,urllib.request,concurrent.futures as cf
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));os.chdir(R)
P='scripts/ev_titles.json';C=json.load(open(P)) if os.path.exists(P) else {}
us=sorted({e['u'] for f in glob.glob('docs/d/*.json') for e in json.load(open(f))['d']['ev']})
def get(u):
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36','Accept-Language':'en,zh;q=0.8'}),timeout=15)
        b=r.read(400000).decode(r.headers.get_content_charset() or 'utf-8','replace')
        m=re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)',b,re.I) or re.search(r'<title[^>]*>(.*?)</title>',b,re.I|re.S)
        t=html.unescape(' '.join(m.group(1).split()))[:140] if m else ''
        return u,t
    except Exception as e: return u,''
todo=[u for u in us if not C.get(u)]
with cf.ThreadPoolExecutor(12) as ex:
    for u,t in ex.map(get,todo):
        if t and not re.search(r'just a moment|access denied|attention required|403|404|not found|robot',t,re.I): C[u]=t
json.dump(C,open(P,'w'),ensure_ascii=False,indent=1)
open('docs/evt.js','w').write('window.EVT='+json.dumps(C,ensure_ascii=False)+';')
print(len(us),'urls,',sum(1 for u in us if C.get(u)),'titled')
