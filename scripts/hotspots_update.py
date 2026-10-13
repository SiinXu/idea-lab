#!/usr/bin/env python3
"""Merge new hotspot items (JSON list via file arg or stdin) into data/hotspots.json (append-only),
rebuild docs/hotspots/data.js (10 languages), commit + push if changed.
Item: {"title": zh, "summary": zh, "links": [...], "topic": optional slug}. Flags: --no-push, --rebuild-only"""
import json,os,sys,hashlib,re,subprocess,datetime
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));os.chdir(R)
DP='data/hotspots.json';CP='scripts/hotspots_cache.json'
SH=datetime.timezone(datetime.timedelta(hours=8))
args=[a for a in sys.argv[1:] if not a.startswith('--')];fl=set(a for a in sys.argv[1:] if a.startswith('--'))
db=json.load(open(DP)) if os.path.exists(DP) else {'lastUpdated':None,'items':[]}
norm=lambda u:re.sub(r'[?#].*$','',u.strip().lower()).rstrip('/').replace('http://','https://').replace('://www.','://')
new=[]
if '--rebuild-only' not in fl:
    raw=open(args[0]).read() if args else sys.stdin.read()
    new=json.loads(raw) if raw.strip() else []
    if isinstance(new,dict): new=new.get('items',[new])
seenL={norm(l) for x in db['items'] for l in x['links']};seenT={x.get('topic') for x in db['items'] if x.get('topic')}
seenTi={re.sub(r'\W','',x['title'].lower()) for x in db['items']}
now=datetime.datetime.now(SH).isoformat(timespec='seconds');added=0
for x in new:
    links=[l for l in x.get('links',[]) if l.startswith('http')]
    if not links or not x.get('title'): continue
    tk=re.sub(r'\W','',x['title'].lower())
    if any(norm(l) in seenL for l in links) or (x.get('topic') and x['topic'] in seenT) or tk in seenTi: continue
    id=hashlib.sha1(norm(links[0]).encode()).hexdigest()[:10]
    db['items'].append({'id':id,'title':x['title'],'summary':x.get('summary',''),'links':links,'topic':x.get('topic',''),'firstSeen':now})
    seenL|={norm(l) for l in links};seenT.add(x.get('topic'));seenTi.add(tk);added+=1
if added or not db['lastUpdated']: db['lastUpdated']=now
elif new: db['lastChecked']=now
db['lastChecked']=now
os.makedirs('data',exist_ok=True);json.dump(db,open(DP,'w'),ensure_ascii=False,indent=1)
# translate
cache=json.load(open(CP)) if os.path.exists(CP) else {}
import opencc;cc=opencc.OpenCC('s2t');T=None
L=['ja','ko','ms','vi','fr','es','de']
def tr(s,f,t):
    global T
    k=f+'|'+t+'|'+s
    if k not in cache:
        if T is None: import argostranslate.translate as T
        cache[k]=T.translate(s,f,t)
    return cache[k]
def multi(zh):
    if not zh: return {}
    en=tr(zh,'zh','en');d={'zh-Hans':zh,'zh-Hant':cc.convert(zh),'en':en}
    for l in L: d[l]=tr(en,'en',l)
    return d
UI={'title':'技术热点雷达','sub':'每 15 分钟自动更新，历史条目永久保留。给每条打状态、写备注，助手会读取并采取下一步。','upd':'最后更新','chk':'最后检查','new':'新','src':'来源','st':'状态','none':'未标记','interested':'感兴趣','todo':'要做','done':'已做','ignore':'忽略','note':'备注','save':'保存','saved':'已保存到云端','local':'仅存本机（未解锁）','pass':'输入口令以同步备注到云端','unlock':'解锁','lock':'退出','err':'保存失败，已存本机','mt':'非中文内容为机器翻译','back':'返回 Idea Lab','first':'首次发现','all':'全部','hideIg':'隐藏已忽略','tz':'上海时间','items':'条','marked':'已标记'}
ui={k:multi(v) for k,v in UI.items()}
items=[dict(x,t=multi(x['title']),s=multi(x['summary'])) for x in db['items']]
json.dump(cache,open(CP,'w'),ensure_ascii=False)
os.makedirs('docs/hotspots',exist_ok=True)
out='window.HS='+json.dumps({'lastUpdated':db['lastUpdated'],'lastChecked':db.get('lastChecked'),'ui':ui,'items':items},ensure_ascii=False)+';'
p='docs/hotspots/data.js'
if not os.path.exists(p) or open(p).read()!=out: open(p,'w').write(out)
print(json.dumps({'added':added,'total':len(db['items']),'lastUpdated':db['lastUpdated']}))
if '--no-push' in fl or (added==0 and '--rebuild-only' not in fl): sys.exit()
subprocess.run(['git','add',DP,CP,'docs/hotspots'],check=True)
if subprocess.run(['git','diff','--cached','--quiet']).returncode:
    subprocess.run(['git','commit','-qm',f'hotspots: +{added} ({now})'],check=True)
    subprocess.run(['git','pull','-q','--rebase'],check=True);subprocess.run(['git','push','-q'],check=True);print('pushed')
