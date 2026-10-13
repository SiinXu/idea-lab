import json,os,sys
sys.path.insert(0,os.path.dirname(__file__))
from ideas import I
from extra import PB,RK
from green import G
from cn import C,CP
from params import P
from detail import build
import re,markdown
I=I+G+C
P.update(dict(CP))
import argostranslate.translate as T
import opencc
cc=opencc.OpenCC('s2t')
CP='scripts/cache.json'
cache=json.load(open(CP)) if os.path.exists(CP) else {}
L=['ja','ko','ms','vi','fr','es','de']
def tr(s,f,t):
    k=f+'|'+t+'|'+s
    if k not in cache: cache[k]=T.translate(s,f,t)
    return cache[k]
def multi(zh):
    en=tr(zh,'zh','en')
    d={'zh-Hans':zh,'zh-Hant':cc.convert(zh),'en':en}
    for l in L: d[l]=tr(en,'en',l)
    return d
F=['tag','t','p','w','m','mo','au','r','k']
out=[]
for n,x in enumerate(I):
    y={'id':x['id'],'sec':x['sec'],'ev':x['ev'],'s':x['s']}
    for f in F: y[f]=multi(x[f])
    out.append(y); print(n,flush=True)
    json.dump(cache,open(CP,'w'),ensure_ascii=False)
pb=[{'t':multi(a),'d':multi(b)} for a,b in PB]
rk=[{'t':multi(a),'d':multi(b)} for a,b in RK]
json.dump(cache,open(CP,'w'),ensure_ascii=False)
open('docs/data.js','w').write('window.DATA='+json.dumps({'ideas':out,'pb':pb,'rk':rk},ensure_ascii=False)+';')
# 详情页
md=open('/workspace/biz-greenfield/top3-detailed.md').read()
parts=re.split(r'\n(?=# \d\. )',md)
DEEP={}
for pt in parts[1:]:
    name=pt.split('—')[0].split('.',1)[1].strip().lower()
    body=pt.split('\n# 一页对照')[0]
    DEEP[name]=markdown.markdown(body.split('\n',1)[1],extensions=['tables'])
os.makedirs('docs/d',exist_ok=True)
tpl=open('scripts/idea.html').read()
def lines(o,S):
    if isinstance(o,str):
        for ln in o.split('\n'):
            if re.search('[\u4e00-\u9fff]',ln): S.add(ln)
    elif isinstance(o,dict): [lines(v,S) for v in o.values()]
    elif isinstance(o,(list,tuple)): [lines(v,S) for v in o]
for n,x in enumerate(I):
    d=build(x,P[x['id']]);S=set();lines(d,S)
    trm={l:{} for l in ['zh-Hant','en']+L}
    for z in S:
        en=tr(z,'zh','en');trm['en'][z]=en;trm['zh-Hant'][z]=cc.convert(z)
        for l in L: trm[l][z]=tr(en,'en',l)
    d['deep']=DEEP.get(x['id'],'')
    json.dump({'d':d,'tr':trm},open(f"docs/d/{x['id']}.json",'w'),ensure_ascii=False)
    os.makedirs(f"docs/idea/{x['id']}",exist_ok=True)
    open(f"docs/idea/{x['id']}/index.html",'w').write(tpl.replace('__ID__',x['id']).replace('__TITLE__',x['t']))
    json.dump(cache,open(CP,'w'),ensure_ascii=False);print('detail',n,flush=True)
print('done')
