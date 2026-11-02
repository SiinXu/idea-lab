#!/usr/bin/env python3
"""Hourly heat collector -> data/heat/YYYY-MM.jsonl (append-only).
Stores ONLY: title, link, raw heat number, rank, percentile, source, timestamp. No user names/avatars/comments.
Usage: heat_collect.py [--x x.json] [--dry-run] [--only hn,v2ex]
Add a source: write fetch_<name>() returning [{"title","link","raw"}] ordered by rank, register it in SOURCES.
Phase 2 slots (not enabled): reddit (official OAuth API only), producthunt (GraphQL v2, non-commercial).
Never: xiaohongshu / weibo / douyin (robots Disallow, no public API)."""
import json,os,sys,re,time,datetime,urllib.request,xml.etree.ElementTree as ET
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));os.chdir(R)
UA={'User-Agent':'IdeaLab-heat/1.0 (+https://ideas.incidental.site)'}
BLOCK=re.compile(r'(xiaohongshu|xhslink|weibo\.(com|cn)|douyin|iesdouyin)',re.I)
def get(u,h=None,t=20):
    if BLOCK.search(u): raise RuntimeError('blocked source')
    r=urllib.request.Request(u,headers={**UA,**(h or {})});return urllib.request.urlopen(r,timeout=t).read()
def fetch_hn():
    ids=json.loads(get('https://hacker-news.firebaseio.com/v0/topstories.json'))[:30];out=[]
    for i in ids:
        x=json.loads(get(f'https://hacker-news.firebaseio.com/v0/item/{i}.json'))
        if x and x.get('title'):out.append({'title':x['title'],'link':x.get('url') or f'https://news.ycombinator.com/item?id={i}','raw':x.get('score',0),'disc':f'https://news.ycombinator.com/item?id={i}'})
    return out
def fetch_v2ex():
    return [{'title':x['title'],'link':x['url'],'raw':x.get('replies',0)} for x in json.loads(get('https://www.v2ex.com/api/topics/hot.json'))]
def fetch_gtrends():
    out=[]
    for geo in ('US','GB'):
        root=ET.fromstring(get(f'https://trends.google.com/trending/rss?geo={geo}'));ns={'ht':'https://trends.google.com/trending/rss'}
        for it in root.iter('item'):
            tr=(it.findtext('ht:approx_traffic',default='0',namespaces=ns) or '0');n=int(re.sub(r'\D','',tr) or 0)
            nu=it.find('ht:news_item/ht:news_item_url',ns)
            out.append({'title':it.findtext('title'),'link':(nu.text if nu is not None else it.findtext('link')),'raw':n,'geo':geo})
    return out
def fetch_github():
    since=(datetime.date.today()-datetime.timedelta(days=7)).isoformat();h={'Accept':'application/vnd.github+json'}
    if os.environ.get('GITHUB_TOKEN'):h['Authorization']='Bearer '+os.environ['GITHUB_TOKEN']
    d=json.loads(get(f'https://api.github.com/search/repositories?q=created:%3E{since}&sort=stars&order=desc&per_page=30',h))
    return [{'title':x['full_name']+(' — '+x['description'][:120] if x.get('description') else ''),'link':x['html_url'],'raw':x['stargazers_count']} for x in d.get('items',[])]
def load_x(path):
    """x.json = raw output of x.search_news (Bot routine). Keep only story name + url."""
    s=open(path).read();s=s[s.find('{'):s.rfind('}')+1];d=json.loads(s).get('data',[])
    return [{'title':x['name'],'link':x['url'],'raw':len(d)-i} for i,x in enumerate(d) if x.get('name') and x.get('url')]
SOURCES={'hn':fetch_hn,'v2ex':fetch_v2ex,'gtrends':fetch_gtrends,'github':fetch_github}  # phase 2: 'reddit','producthunt'
def pct(rows):
    """percentile within this round by raw value (ties by rank) -> p 0..100"""
    N=len(rows);order=sorted(range(N),key=lambda i:(-rows[i]['raw'],i))
    for r,i in enumerate(order,1):rows[i]['rank']=r;rows[i]['p']=round(100*(1-(r-1)/N),1)
    return rows
def main():
    a=sys.argv[1:];dry='--dry-run' in a;xp=a[a.index('--x')+1] if '--x' in a else None
    only=set(a[a.index('--only')+1].split(',')) if '--only' in a else None
    ts=datetime.datetime.now(datetime.timezone.utc).replace(minute=0,second=0,microsecond=0).isoformat().replace('+00:00','Z')
    lines=[];stat={}
    jobs=[(k,f) for k,f in SOURCES.items() if not only or k in only]
    if xp:jobs.append(('x',lambda:load_x(xp)))
    for k,f in jobs:
        try:
            rows=pct([r for r in f() if r.get('title') and r.get('link','').startswith('http') and not BLOCK.search(r['link'])])
            for r in rows:lines.append({'ts':ts,'src':k,'title':r['title'][:200],'link':r['link'],'rank':r['rank'],'p':r['p'],'raw':r['raw'],**({'disc':r['disc']} if r.get('disc') else {}),**({'geo':r['geo']} if r.get('geo') else {})})
            stat[k]=len(rows)
        except Exception as e:stat[k]='ERR '+str(e)[:80]
    p=f'data/heat/{ts[:7]}.jsonl'
    if not dry:
        seen=set()
        if os.path.exists(p):
            for l in open(p):
                try:o=json.loads(l);seen.add((o['ts'],o['src'],o['link']))
                except:pass
        new=[l for l in lines if (l['ts'],l['src'],l['link']) not in seen]
        with open(p,'a') as fh:
            for l in new:fh.write(json.dumps(l,ensure_ascii=False)+'\n')
        stat['written']=len(new)
    print(json.dumps({'ts':ts,'file':p,'sources':stat},ensure_ascii=False))
    if all(isinstance(v,str) for k,v in stat.items() if k!='written'):sys.exit(2)
main()
