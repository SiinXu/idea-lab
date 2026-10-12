import json,os,sys
sys.path.insert(0,os.path.dirname(__file__))
from ideas import I
from extra import PB,RK
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
open('site/data.js','w').write('window.DATA='+json.dumps({'ideas':out,'pb':pb,'rk':rk},ensure_ascii=False)+';')
print('done')
