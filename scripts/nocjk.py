"""Non-Chinese locales must contain no Chinese (hard rule 2026-10-16).
scrub(obj): walks generated data; in every locale map ({'zh-Hans':..,'en':..}) or translation tree (tr[L]) for a
non-zh locale, removes Chinese runs (ja: only characters that do not exist in Japanese, i.e. not in CP932).
Standalone:  python3 scripts/nocjk.py   (cleans docs/data.js, docs/hotspots/data.js, docs/d/*.json in place)."""
import json,re,glob,sys,os
CJK=re.compile(r'[\u3400-\u9fff\uf900-\ufaff]')
NON=('en','ja','ko','ms','vi','fr','es','de')
FIX={'X/小红书涨粉 → 付费社群 ¥99/年 → 课程。':'Grow followers on X and lifestyle apps → paid community ¥99/yr → course.'}
def _ja_ok(ch):
    try: ch.encode('cp932'); return True
    except UnicodeEncodeError: return False
def clean(v,L):
    if not isinstance(v,str) or not CJK.search(v): return v
    if L=='ja':
        if all(_ja_ok(c) for c in CJK.findall(v)): return v
        v=''.join(c for c in v if not CJK.match(c) or _ja_ok(c))
    else:
        v=re.sub(r'[（(《「][^）)》」]*[\u3400-\u9fff][^）)》」]*[）)》」]','',v)
        v=re.sub(r'[\u3400-\u9fff\uf900-\ufaff\u3000-\u303f\uff0c\uff1a\uff1b\uff01\uff1f「」《》【】]+',' ',v)
    v=re.sub(r'\s+([,.;:!?)])',r'\1',v); v=re.sub(r'\s{2,}',' ',v).strip()
    return v
def _deep(o,L):
    if isinstance(o,str): return clean(o,L)
    if isinstance(o,list): return [_deep(x,L) for x in o]
    if isinstance(o,dict): return {k:_deep(x,L) for k,x in o.items()}
    return o
def scrub(o):
    if isinstance(o,dict):
        if 'en' in o and any(k in o for k in ('zh-Hans','zh','zh-CN')):
            src=o.get('zh-Hans') or o.get('zh') or o.get('zh-CN')
            for L in NON:
                if L in o:
                    if L=='en' and src in FIX: o['en']=FIX[src]
                    elif L!='en' and src in FIX and isinstance(o[L],str) and CJK.search(o[L]) and L!='ja': o[L]=FIX[src]
                    else: o[L]=_deep(o[L],L)
        for k in list(o):
            if k=='tr' and isinstance(o[k],dict):
                for L in list(o[k]):
                    if L in NON: o[k][L]=_deep(o[k][L],L)
            else: scrub(o[k])
    elif isinstance(o,list):
        for x in o: scrub(x)
    return o
def _js(p,var):
    s=open(p).read(); pre=f'window.{var}='; assert s.startswith(pre)
    d=scrub(json.loads(s[len(pre):].rstrip().rstrip(';')))
    open(p,'w').write(pre+json.dumps(d,ensure_ascii=False)+';')
if __name__=='__main__':
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
    _js('docs/data.js','DATA'); _js('docs/hotspots/data.js','HS')
    for p in glob.glob('docs/d/*.json'):
        d=scrub(json.load(open(p))); json.dump(d,open(p,'w'),ensure_ascii=False)
    print('nocjk ok')
