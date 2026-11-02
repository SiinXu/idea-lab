#!/usr/bin/env python3
"""Hot-topic -> product ideas, two SEPARATE model calls (generator, then a different scorer call), done by the Bot routine.
  ideas_gen.py prompt            -> out/ideas-gen-prompt.md   (top-20 rising/new topics + rules)  -> model call #1 writes gen.json
  ideas_gen.py score gen.json    -> out/ideas-score-prompt.md (ideas that passed keyword filter)   -> model call #2 writes score.json
  ideas_gen.py apply gen.json score.json -> data/hot-ideas.json (append) + docs/hotspots/ideas.js (10 langs, shown only score>=7)
gen.json: [{"topic","who","pain","why_now","mvp","money","not_do","title","evidence":[url,...]}]
score.json: [{"i":index,"evidence":0-3,"two_weeks":0-2,"money":0-2,"reuse":0-2,"novel":0-1,"forbidden":false,"why":"..."}]"""
import json,os,re,sys,hashlib,datetime
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));os.chdir(R);sys.path.insert(0,'scripts')
F=['who','pain','why_now','mvp','money','not_do']
BAN=re.compile(r'赌|博彩|casino|gambl|bet(ting)?\b|成人|porn|nsfw|色情|刷量|刷粉|假粉|fake (followers|reviews)|假评论|spam|群发|假稀缺|盗版|pirac|crack|破解|荐股|概念股|推.{0,4}股票|股票推荐|stock tips?|signals? group|换汇|逃税|tax evasion|代收|代付|payment proxy|爬.{0,4}个人|scrap\w* (personal|user) data|漏洞套利|exploit arbitrage|airdrop farm|撸毛',re.I)
DEAD={'skillshot','memcut','nitter','eigvst','iadump','takes'}
def grams(t):t=re.sub(r'\W','',t.lower());return {t[i:i+3] for i in range(max(1,len(t)-2))}
def jac(a,b):return len(a&b)/len(a|b) if a and b else 0
def heat():
    s=open('docs/hotspots/heat.js').read();return json.loads(s[s.index('=')+1:].rstrip(';'))
DB='data/hot-ideas.json';db=json.load(open(DB)) if os.path.exists(DB) else {'items':[]}
os.makedirs('out',exist_ok=True);cmd=sys.argv[1] if len(sys.argv)>1 else ''
if cmd=='prompt':
    H=heat();tops=sorted(H['topics'],key=lambda x:(-x['rising'],-x['heat']))[:20]
    lines=[f"- id={x['id']} heat={x['heat']} rising={x['rising']} title={x['title']} sources={json.dumps(x['links'],ensure_ascii=False)}" for x in tops]
    open('out/ideas-gen-prompt.md','w').write(f"""你是产品点子生成器。对下面每个热点话题，最多给 3 个点子（不合适就 0 个），中文输出 JSON 数组，字段：
topic(话题 id), title(≤20 字), who(谁), pain(什么痛), why_now(为什么现在), mvp(两周 MVP), money(怎么收钱), not_do(不做什么), evidence(≥1 条，必须来自该话题 sources 的链接)。
禁区（命中直接不出）：赌博、成人、刷量假粉、spam、假稀缺或假评论、盗版、荐股、换汇或逃税、代收代付、爬个人数据、漏洞套利。
不复活：{', '.join(sorted(DEAD))}。Siin 现有资产：Idea Lab、设计规范库、UI Hub、Skills Lab、刷题站、Cloudflare Workers。
话题：
"""+'\n'.join(lines));print('out/ideas-gen-prompt.md',len(tops))
elif cmd=='score':
    g=json.load(open(sys.argv[2]));keep=[(i,x) for i,x in enumerate(g) if not BAN.search(json.dumps(x,ensure_ascii=False))]
    open('out/ideas-score-prompt.md','w').write("""你是独立评审（不是出点子的那一方）。逐条打分，输出 JSON 数组 [{"i","evidence":0-3,"two_weeks":0-2,"money":0-2,"reuse":0-2,"novel":0-1,"forbidden":bool,"why"}]。
evidence：带 X/HN/V2EX/Reddit 真实讨论链接 3 分，只有官方或产品叙事 1 分。forbidden：是否落入 赌博/成人/刷量假粉/spam/假稀缺假评论/盗版/荐股/换汇逃税/代收代付/爬个人数据/漏洞套利 任一类。
"""+'\n'.join(f"[{i}] "+json.dumps(x,ensure_ascii=False) for i,x in keep));print('out/ideas-score-prompt.md',len(keep),'of',len(g))
elif cmd=='apply':
    g=json.load(open(sys.argv[2]));sc={s['i']:s for s in json.load(open(sys.argv[3]))};H=heat();T={x['id']:x for x in H['topics']}
    now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds');old=[grams(x['title']) for x in db['items']];rep={'in':len(g),'ban':0,'dead':0,'dup':0,'nolink':0,'missing':0,'low':0,'added':0}
    for i,x in enumerate(g):
        s=sc.get(i);blob=json.dumps(x,ensure_ascii=False)
        if BAN.search(blob) or not s or s.get('forbidden'):rep['ban']+=1;continue
        if any(d in blob.lower() for d in DEAD):rep['dead']+=1;continue
        if not all(x.get(k) for k in F+['title']):rep['missing']+=1;continue
        allowed=set(T.get(x.get('topic'),{}).get('links',{}).values());ev=[u for u in x.get('evidence',[]) if u in allowed]
        if not ev:rep['nolink']+=1;continue
        tot=sum(int(s.get(k,0)) for k in ['evidence','two_weeks','money','reuse','novel'])
        gg=grams(x['title'])
        if any(jac(gg,o)>=0.6 for o in old):rep['dup']+=1;continue
        db['items'].append({**{k:x[k] for k in ['topic','title']+F},'evidence':ev,'score':tot,'parts':{k:s.get(k) for k in ['evidence','two_weeks','money','reuse','novel']},'why':s.get('why',''),'shown':tot>=7,'at':now,'id':hashlib.sha1((x['topic']+x['title']).encode()).hexdigest()[:10]})
        old.append(gg);rep['added']+=1;rep['low']+=tot<7
    json.dump(db,open(DB,'w'),ensure_ascii=False,indent=1)

    print(json.dumps(rep,ensure_ascii=False))
elif cmd=='build':
    pass
else:print(__doc__);sys.exit(1)
if cmd in('apply','build'):
    import opencc,argostranslate.translate as AT;cc=opencc.OpenCC('s2t');CP='scripts/hotspots_cache.json';cache=json.load(open(CP))
    def tr(s,f,t):
        k=f+'|'+t+'|'+s
        if k not in cache:cache[k]=AT.translate(s,f,t)
        return cache[k]
    def multi(z):
        en=tr(z,'zh','en');d={'zh-Hans':z,'zh-Hant':cc.convert(z),'en':en}
        for l in ['ja','ko','ms','vi','fr','es','de']:d[l]=tr(en,'en',l)
        return d
    from nocjk import scrub
    shown=[x for x in db['items'] if x['shown']][-60:]
    out=[{'id':x['id'],'topic':x['topic'],'score':x['score'],'at':x['at'],'evidence':x['evidence'],**{k:multi(x[k]) for k in ['title']+F}} for x in shown]
    json.dump(cache,open(CP,'w'),ensure_ascii=False)
    open('docs/hotspots/ideas.js','w').write('window.HIDEAS='+json.dumps(scrub({'lastUpdated':datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),'items':out}),ensure_ascii=False,separators=(',',':'))+';');print('ideas.js',len(out))
