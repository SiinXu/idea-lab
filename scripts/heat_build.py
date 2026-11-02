#!/usr/bin/env python3
"""Build docs/hotspots/heat.js from data/heat/*.jsonl.
Topic merge: (1) normalized link (same norm() as hotspots_update), (2) title char-3-gram Jaccard >= 0.5
(CJK titles compared after argos zh->en). Stable topic ids in data/heat/topics.json.
Heat(topic,hour) = sum_src w_src * max p ; series = last 14 days hourly ; rising = slope(last 6h) > 0 and heat >= 60."""
import json,os,re,glob,hashlib,datetime,sys
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));os.chdir(R);sys.path.insert(0,'scripts')
W={'x':1.0,'hn':1.0,'gtrends':1.0,'github':0.8,'v2ex':0.6}
TRK=re.compile(r'^(utm_\w+|ref|ref_src|ref_url|s|t|si|fbclid|gclid|mc_cid|mc_eid|igshid|share|source)$',re.I)
def norm(u):
    u=u.strip();b,_,q=u.split('#',1)[0].partition('?')
    b=b.lower().rstrip('/').replace('http://','https://').replace('://www.','://')
    kept=sorted(kv for kv in q.split('&') if kv and not TRK.match(kv.split('=',1)[0]))
    return b+('?'+'&'.join(kept) if kept else '')
CJK=re.compile(r'[\u3400-\u9fff]')
CP='scripts/hotspots_cache.json';cache=json.load(open(CP)) if os.path.exists(CP) else {};T=None;dirty=False
def tr(s,f,t):
    global T,dirty
    k=f+'|'+t+'|'+s
    if k not in cache:
        if T is None: import argostranslate.translate as T
        cache[k]=T.translate(s,f,t);dirty=True
    return cache[k]
STOP=set('the a an of to in on for and or with is are by from at as new how why what your you we i it this that show hn ask'.split())
def grams(t):
    t=re.sub(r'[^\w ]',' ',t.lower());t=' '.join(w for w in t.split() if w not in STOP).replace(' ','')
    return {t[i:i+3] for i in range(max(1,len(t)-2))}
def jac(a,b): return len(a&b)/len(a|b) if a and b else 0
rows=[json.loads(l) for f in sorted(glob.glob('data/heat/*.jsonl')) for l in open(f) if l.strip()]
# r1.1: Google Trends is general-audience -> keep only dev/tech-relevant rows (raw jsonl untouched)
TECH=re.compile(r'\b(ai|a\.i\.|gpt|chatgpt|openai|anthropic|claude|gemini|llm|grok|xai|nvidia|amd|intel|apple|iphone|ipad|mac|macos|ios|android|google|pixel|microsoft|windows|xbox|meta|tesla|spacex|starlink|amazon|aws|azure|cloud|github|linux|software|app|apps|developer|coding|code|programming|python|javascript|rust|api|chip|chips|semiconductor|robot|robotics|startup|crypto|bitcoin|ethereum|cyber|hack|hacker|security|outage|data|tech|samsung|sony|playstation|nintendo|steam|vr|quantum|tiktok|x\.com|twitter|reddit|youtube|discord|whatsapp|instagram|update|beta|launch)\b',re.I)
rows=[r for r in rows if r['src']!='gtrends' or TECH.search(r['title'])]
TP='data/heat/topics.json';tp=json.load(open(TP)) if os.path.exists(TP) else {'byLink':{},'topics':{}}
# link -> existing Idea Lab hotspot topic (reuse slug)
old={}
try:
    for x in json.load(open('data/hotspots.json'))['items']:
        for l in x['links']: old[norm(l)]=x.get('topic') or x['id']
except Exception: pass
def en_title(t): return tr(t,'zh','en') if CJK.search(t) else t
G={tid:grams(en_title(v['title'])) for tid,v in tp['topics'].items()}
for r in rows:
    k=norm(r['link'])
    if k in tp['byLink']: r['topic']=tp['byLink'][k];continue
    g=grams(en_title(r['title']));best=max(G.items(),key=lambda kv:jac(g,kv[1]),default=(None,set()))
    if best[0] and jac(g,best[1])>=0.5: tid=best[0]
    else:
        tid=old.get(k) or 'h'+hashlib.sha1(k.encode()).hexdigest()[:9]
        tp['topics'][tid]={'title':r['title'],'link':r['link'],'first':r['ts']};G[tid]=g
    tp['byLink'][k]=tid;r['topic']=tid
json.dump(tp,open(TP,'w'),ensure_ascii=False,indent=0)
hours=sorted({r['ts'] for r in rows});now=hours[-1] if hours else None
cut=(datetime.datetime.fromisoformat(now.replace('Z','+00:00'))-datetime.timedelta(days=14)).isoformat().replace('+00:00','Z') if now else ''
H=[h for h in hours if h>=cut]
agg={}
for r in rows:
    if r['ts']<cut: continue
    a=agg.setdefault(r['topic'],{}).setdefault(r['ts'],{});a[r['src']]=max(a.get(r['src'],0),r['p'])
links={}
for r in rows:
    d=links.setdefault(r['topic'],{});d.setdefault(r['src'],r.get('disc') or r['link'])
L=['ja','ko','ms','vi','fr','es','de'];import opencc;cc=opencc.OpenCC('s2t')
def multi(t):
    if CJK.search(t): en=tr(t,'zh','en');d={'zh-Hans':t,'zh-Hant':cc.convert(t),'en':en}
    else: en=t;d={'zh-Hans':t,'zh-Hant':t,'en':t}
    for l in L: d[l]=tr(en,'en',l)
    return d
rows_by={}
for r in rows:
    if r['ts']>=cut: rows_by.setdefault(r['topic'],[]).append(r)
out=[]
for tid,byh in agg.items():
    ser=[round(sum(W[s]*p for s,p in byh.get(h,{}).items()),1) for h in H]
    heat=ser[-1] if ser else 0
    last=[v for v in ser[-6:]];rising=len(last)>=2 and last[-1]-last[0]>0 and heat>=60
    src={s:[round(byh.get(h,{}).get(s,0),1) for h in H] for s in W if any(s in byh.get(h,{}) for h in H)}
    last_raw={};prev_raw={}
    for r in rows_by.get(tid,[]):
        if r['ts']==H[-1]: last_raw[r['src']]=max(last_raw.get(r['src'],0),r['raw'])
        elif len(H)>1 and r['ts']==H[-2]: prev_raw[r['src']]=max(prev_raw.get(r['src'],0),r['raw'])
    delta={k:v-prev_raw[k] for k,v in last_raw.items() if k in prev_raw}
    rk={r['src']:r['rank'] for r in rows_by.get(tid,[]) if r['ts']==H[-1]}
    out.append({'raw':last_raw,'delta':delta,'rank':rk,'first':min(r['ts'] for r in rows_by.get(tid,[])) if rows_by.get(tid) else None,'id':tid,'heat':heat,'peak':max(ser),'rising':rising,'n':sum(1 for v in ser if v>0),'series':ser,'src':src,'links':links[tid],'title':tp['topics'][tid]['title']})
out.sort(key=lambda x:(-x['heat'],-sum(x['raw'].values()) if len(H)<2 else -x['peak']));out=out[:80]
for x in out: x['t']=multi(x['title'])
if dirty: json.dump(cache,open(CP,'w'),ensure_ascii=False)
from nocjk import scrub
doc={'updated':now,'lastUpdated':datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),'hours':H,'weights':W,'sources':list(W),'topics':out}
open('docs/hotspots/heat.js','w').write('window.HEAT='+json.dumps(scrub(doc),ensure_ascii=False,separators=(',',':'))+';')
print(json.dumps({'hours':len(H),'topics':len(agg),'shown':len(out),'multiSrc':sum(1 for x in out if len(x['src'])>1),'rising':sum(x['rising'] for x in out)}))
