#!/usr/bin/env python3
"""Dump all hotspot notes (from the Cloudflare Worker) joined with item titles, as JSON to stdout."""
import json,os,urllib.request
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W='https://idea-lab-notes.sinxu-xsy.workers.dev/notes'
n=json.load(urllib.request.urlopen(urllib.request.Request(W,headers={'User-Agent':'idea-lab'}),timeout=15))
db=json.load(open(os.path.join(R,'data/hotspots.json')))
by={x['id']:x for x in db['items']}
print(json.dumps([dict(id=k,title=by.get(k,{}).get('title'),links=by.get(k,{}).get('links'),**v) for k,v in sorted(n.items(),key=lambda kv:kv[1].get('updated',''),reverse=True)],ensure_ascii=False,indent=1))
