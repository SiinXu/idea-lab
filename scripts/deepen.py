# 给详情页加「落地深化」(plus) + 「一键全案 Prompt」；可单独运行（只改 docs/d/*.json），也被 build.py 调用
import json,os,re,sys,glob
sys.path.insert(0,os.path.dirname(__file__))
from deep import DP
MP='一键全案（给任意 AI，复制即用）'
def master(x,d,p):
    cv=d['canvas'];J='；'.join
    L=[f"你是我的一人公司联合创始人兼执行教练。请基于下面这份点子档案，产出一份可以今天就开工的执行方案。",
       f"点子：{x['t']}",f"痛点：{x['p']}",f"目标用户：{x['w']}",f"MVP：{x['m']}",
       "【商业模式画布】",f"价值主张：{J(cv['vp'])}",f"客户细分：{J(cv['cs'])}",f"渠道：{J(cv['ch'])}",f"客户关系：{J(cv['cr'])}",
       f"关键活动：{J(cv['ka'])}",f"关键资源：{J(cv['kr'])}",f"关键伙伴：{J(cv['kp'])}",f"成本结构：{J(cv['cost'])}",f"收入来源：{J(cv['rs'])}",
       "【商业模式】",f"模式：{d['kind']}；收入流：{d['stream']}",f"价格档：{J(t['n']+' '+t['p']+'（'+t['d']+'）' for t in d['tiers'])}",
       f"单位经济（假设）：{J(a+' '+b for a,b in d['ue'])}",
       "【收益估算（全部是假设，不是事实）】",*[f"- {a}" for a in d['assume']],
       f"基准情景月收入：第1月 {d['cur']}{d['rev'][0]['base']:,}，第6月 {d['cur']}{d['rev'][2]['base']:,}，第12月 {d['cur']}{d['rev'][3]['base']:,}（估算）",
       "【风险与砍掉线】",*[f"- {r['n']}：{r['c']}" for r in d['risks']],*[f"- 砍：{k}" for k in d['kills']],
       "【运营】",*[f"- {a}：{b}" for a,b in d['d7']],
       f"首批付费用户：{J(p['f10'])}",f"48 小时验证：{p['t48']}",
       "【自动化】",*[f"- {j}" for j in p['jobs']],f"北极星指标：{p['ns']}",
       "请输出：1) 本周 7 天逐日任务（每天 ≤ 2 小时）；2) 落地页文案（标题、副标题、3 个卖点、FAQ 5 条）；3) 首批 10 个用户的触达话术 3 版；4) 自动化脚本清单与伪代码；5) 用我的真实数据替换上面所有假设数字的方法。",
       "规则：不编造数据和链接；所有数字标注来源或标为[假设]；不承诺收益；遵守平台规则与当地法律。"]
    return '\n'.join(L)
def enrich(x,d):
    p=DP[x['id']]
    d['plus']=dict(f10=p['f10'],must=p['must'],cut=p['cut'],t48=p['t48'],moat=p['moat'],jobs=[j.strip() for j in re.split('；',p['jobs']) if j.strip()],ns=p['ns'])
    pr=[q for q in d['prompts'] if q[0]!=MP]
    d['plus_jobs']=None; d.pop('plus_jobs')
    d['prompts']=pr+[[MP,master(x,d,d['plus'])]]
    return d
def lines(o,S):
    if isinstance(o,str):
        for ln in o.split('\n'):
            if re.search('[\u4e00-\u9fff]',ln): S.add(ln)
    elif isinstance(o,dict): [lines(v,S) for v in o.values()]
    elif isinstance(o,(list,tuple)): [lines(v,S) for v in o]
if __name__=='__main__':
    os.chdir(os.path.join(os.path.dirname(__file__),'..'))
    from ideas import I; from green import G; from cn import C
    import opencc, glob, fasttr
    cc=opencc.OpenCC('s2t'); cache=json.load(open('scripts/cache.json'))
    for extra in glob.glob('/tmp/il_cache_*.json'):
        try: cache.update(json.load(open(extra)))
        except Exception: pass
    Ls=['ja','ko','ms','vi','fr','es','de']
    allx=sorted(I+G+C,key=lambda x:-sum(x['s'])); only=sys.argv[1:]
    J={}; need=set()
    for x in allx:
        if only and x['id'] not in only: continue
        f=f"docs/d/{x['id']}.json"; j=json.load(open(f)); d=enrich(x,j['d']); S=set(); lines(d,S)
        J[f]=(j,d,S); need|={z for z in S if any(z not in j['tr'].get(l,{}) for l in ['en']+Ls)}
    print('ideas',len(J),'new zh lines',len(need),flush=True)
    en=fasttr.batch(sorted(need),'zh','en',cache)
    E=set(en.values())|{j['tr']['en'][z] for f,(j,d,S) in J.items() for z in S if z in need and z in j['tr']['en']}
    for l in Ls: fasttr.batch(sorted(E),'en',l,cache)
    for f,(j,d,S) in J.items():
        trm=j['tr']
        for z in S:
            if z not in need: continue
            e=trm['en'].get(z) or en[z]; trm['en'][z]=e; trm['zh-Hant'][z]=cc.convert(z)
            for l in Ls:
                if z not in trm[l]: trm[l][z]=fasttr.batch([e],'en',l,cache)[e]
        json.dump({'d':d,'tr':trm},open(f,'w'),ensure_ascii=False)
    json.dump(cache,open('scripts/cache.json','w'),ensure_ascii=False)
    print('done',flush=True)
