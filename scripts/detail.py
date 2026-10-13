# 从点子字段 + params 生成详情页结构（中文，全部数字为 [假设]）
UNVER={'www.xhllsys.com','blog.csdn.net','toolsy.io','www.insightagent.app','www.xianyunav.com','www.etsy.com','alternativeto.net','openai.com','theresanaiforthat.com','www.judge.me','hypefury.com'}
KIND={'svc':'按单服务','one':'一次性产品','sub':'订阅 SaaS','aff':'流量/联盟','course':'课程社群'}
def interp(tr):
    pts={1:tr[0],3:tr[1],6:tr[2],12:tr[3]};ks=[1,3,6,12];out=[]
    for m in range(1,13):
        for a,b in zip(ks,ks[1:]):
            if a<=m<=b: out.append(pts[a]+(pts[b]-pts[a])*(m-a)/(b-a));break
    return out
SC={'cons':(.5,.6),'base':(1,1),'opt':(1.8,1.4)}
def model(q):
    res={}
    for s,(ft,fc) in SC.items():
        tr=[v*ft for v in interp(q['traffic'])];act=0;rev=[];cust=[]
        for v in tr:
            new=v*q['conv']*fc
            if q['kind']=='sub': act=act*0.92+new;r=act*q['arpu']
            else: r=new*q['arpu'];act=new
            rev.append(round(r));cust.append(round(act,1))
        res[s]=dict(rev=rev,cust=cust,traffic=[round(v) for v in tr])
    return res
def build(x,q):
    c=q['cur'];k=q['kind'];M=model(q);b=M['base']
    gp=q['arpu']*q['gm']
    pay=('%.1f 个月'%(q['cac']/gp)) if k=='sub' else ('首单即回本' if gp>=q['cac'] else '约 %.1f 单回本'%(q['cac']/gp))
    tiers=[dict(n=a,p=(c+v if v not in('0','~') else ('免费' if v=='0' else '按成交')),d=d) for a,v,d in q['tiers']]
    stream={'svc':'按单收费 + 高阶套餐 + 复购/月度维护','one':'一次性售卖 + 升级包 + 团队授权','sub':'月/年订阅 + 用量超额 + 团队席位','aff':'联盟佣金 + 赞助位 + 少量付费产品','course':'课程/社群门票 + 进阶批改 + 企业内训'}[k]
    canvas=dict(
      kp=[q['pt'],'收款 MoR（Creem / Lemon Squeezy / Paddle）','LLM API 与托管（Cloudflare / Vercel）'],
      ka={'svc':['接单与交付流水线','作品集与案例沉淀','冷外联与社区曝光'],'one':['持续上新与迭代','作品展示与 SEO','市场平台上架'],'sub':['产品稳定运行与告警','新功能迭代','留存与流失回访'],'aff':['批量产出高质量内容','SEO 与收录监控','联盟与赞助商谈判'],'course':['课程内容打磨','社群运营与作业反馈','招生内容投放']}[k],
      kr=['AI 编码代理 + 可复用模板/组件','提示词与自动化脚本库','独立域名与邮件名单',q['comp'].split('、')[0]+' 之外的差异化：速度与审美'],
      vp=[x['p'],x['m']],
      cr={'svc':['1 对 1 交付，24–48h SLA','交付后 7 天免费修改 1 轮'],'one':['自助购买、自动交付','邮件更新通知'],'sub':['自助开通 + 邮件引导','产品内反馈 + 月度更新日志'],'aff':['内容自助浏览','邮件周报维系'],'course':['社群陪伴 + 作业点评','结营复盘与转介绍']}[k],
      ch=q['ch'],cs=[x['w']],
      cost=['域名 ~$12/年；托管 $0–20/月','LLM/API ≈ 收入的 %d%%'%round((1-q['gm'])*100),'工具订阅 ~$30/月；收款费 ~4–5%/单','获客：CAC ≈ %s%s/客 [假设]'%(c,q['cac'])],
      rs=[t['n']+' '+t['p'] for t in tiers]+[stream])
    ue=[('ARPU',f"{c}{q['arpu']}"+('/月' if k=='sub' else '/单')),('CAC',f"{c}{q['cac']}"),('毛利率',f"{round(q['gm']*100)}%"),('回本',pay),('转化率',f"{q['conv']*100:.1f}%"),('模式',KIND[k])]
    rev=[dict(m=m,**{s:M[s]['rev'][m-1] for s in M},t=b['traffic'][m-1],cu=b['cust'][m-1]) for m in (1,3,6,12)]
    assume=[f"基准月访问：第1月 {q['traffic'][0]:,}，第3月 {q['traffic'][1]:,}，第6月 {q['traffic'][2]:,}，第12月 {q['traffic'][3]:,}",
      f"访问→付费转化 {q['conv']*100:.1f}%，ARPU {c}{q['arpu']}"+('；订阅月流失 8%（客户累积）' if k=='sub' else '；按当月新成交计'),
      "保守 = 流量×0.5、转化×0.6；乐观 = 流量×1.8、转化×1.4","全部为估算，未经验证；不是承诺或预测"]
    L=lambda a,b,cc:dict(l=a,i=b,c=cc)
    legal={'svc':L(2,2,'合同写清交付范围、责任上限与退款条款；不碰违法客户'),'one':L(1,2,'只用可商用素材，写清授权范围'),'sub':L(2,2,'隐私政策 + 数据删除承诺；按 GDPR/PDPA 最小化收集'),'aff':L(2,2,'联盟链接显式披露；内容不做投资/医疗建议'),'course':L(2,2,'课程宣传不承诺结果；退款规则前置')}[k]
    risks=[dict(n='法律/合规',**legal),
      dict(n='平台依赖',l=2,i=3,c='至少 2 个获客渠道 + 自有邮件名单；主渠道：'+q['ch'][0]),
      dict(n='收款',l=2,i=3,c='首选 MoR（Creem / Lemon Squeezy）代缴税；准备 Paddle 备用；首月小额测试提现'),
      dict(n='竞争',l=3 if k in('sub','aff') else 2,i=2,c='对手：'+q['comp']+'。打细分人群 + 交付速度 + 审美，不拼功能数量'),
      dict(n='执行',l=2,i=2,c=x['r']+' 每周固定 '+str(q['hrs'])+' 小时，按 D7/D14/D30 复盘')]
    kills=[x['k'],f"D14 累计访问 < {round(q['traffic'][0]*0.3):,} → 换渠道或砍",f"D30 付费 < {max(1,round(M['cons']['cust'][0]))} 个 → 停止新功能，只做获客实验 1 周",f"第 3 个月月收入 < {c}{M['cons']['rev'][2]:,}（保守线）→ 归档进失败档案"]
    d7=[('D1','证据：3 个竞品定价页 + 3 条需求帖截图；确定一句话定位'),('D2','独立域名落地页 + 等待名单 + 价格表（'+' / '.join(t['n']+' '+t['p'] for t in tiers)+'）'),('D3','用 AI 编码代理搭核心功能：'+x['m']),('D4','核心功能跑通 + 3 个真实样例/作品'),('D5','接入 Creem/Lemon Squeezy 收款 + 自动交付邮件'),('D6','准备首发内容：1 条 thread + 1 篇长文 + 3 张前后对比图'),('D7','首发：'+q['ch'][0]+' + '+q['ch'][1]+'；记录访问与询价')]
    w=[('第 2 周 (D8–14)','每天 1 条内容 + 10 次触达；收集 5 个用户反馈，修最痛的 1 个问题','访问 '+f"{round(q['traffic'][0]*.4):,}"+' · 等待名单/询价 ≥ 10'),
       ('第 3 周 (D15–21)','上线第二渠道：'+q['ch'][2]+'；做 3 篇 SEO 长尾页；加推荐/返利','首单 ≥ 1 · 转化 ≥ '+f"{q['conv']*50:.1f}%"),
       ('第 4 周 (D22–30)','复盘漏斗；涨价或加高阶档；把重复动作写成脚本自动化','月收入 ≥ '+f"{c}{M['cons']['rev'][0]:,}"+'（保守线）')]
    cal=[['周一','需求帖/痛点拆解（'+q['ch'][0]+'）'],['周二','案例或前后对比图'],['周三','SEO 长尾页 1 篇'],['周四','过程直播：build in public 数据'],['周五','用户故事/FAQ 合集'],['周末','周报 + 下周选题']]
    kpi=[('MVP (D1–7)','落地页上线、3 个样例、收款跑通'),('验证 (D8–30)',f"访问 {q['traffic'][0]:,}/月 · 付费 {max(1,round(b['cust'][0]))}+ · CAC ≤ {c}{q['cac']}"),('增长 (M2–6)',f"月收入 {c}{b['rev'][5]:,} · 渠道 ≥ 2 · 自动化率 ≥ 70%"),('复利 (M7–12)',f"月收入 {c}{b['rev'][11]:,} · 邮件名单 ≥ {round(q['traffic'][3]*0.05):,}")]
    human={'svc':[0,0,1,1,0,1],'one':[0,0,0,1,0,1],'sub':[0,0,0,0,0,1],'aff':[0,0,1,0,0,1],'course':[0,0,1,1,0,1]}[k]
    steps=['线索/数据采集（定时抓取 + 表单）','AI 生成草稿/报告（'+x['au'][:40]+'）','人工抽查与润色','交付/发布','收款与发票（MoR 自动）','周报复盘与选题']
    pipe=[dict(s=s,h=h) for s,h in zip(steps,human)]
    tools=['Claude/GPT API','Playwright / cron（GitHub Actions）','Astro 或 Next.js 静态站','Creem / Lemon Squeezy','Beehiiv / Resend 邮件','Notion 实验日志']
    stack='Astro + Cloudflare Pages' if k in('aff','one','course') else 'Next.js + Supabase + Cloudflare'
    pr=[('搭建（给编码代理）',f"你是资深全栈工程师。为「{x['t']}」做一个可上线 MVP。\n目标用户：{x['w']}\n核心功能：{x['m']}\n价格档：{'；'.join(t['n']+' '+t['p']+' '+t['d'] for t in tiers)}\n技术栈：{stack}；收款用 Creem 或 Lemon Squeezy 托管结账；支持 10 种语言（简繁英日韩马越法西德），按浏览器语言自动默认。\n视觉：参考我的 UI 资源库与 frontend-design / taste skill，暗色+亮色，单一强调色，有克制的动效；禁止紫色渐变 AI 味。\n交付：可运行代码、README、部署步骤、Playwright 桌面+手机×明暗截图。先给文件结构与数据模型，确认后再写代码。"),
       ('内容（给写作 AI）',f"你是 {q['ch'][0]} 上的增长写手。为「{x['t']}」写 7 天内容：\n痛点：{x['p']}\n受众：{x['w']}\n每天 1 条：钩子一句 + 3 个具体数据/例子 + 1 个软性 CTA（等待名单链接）。\n规则：不夸大、不承诺收益，数字必须注明来源或标为示例；附 3 个可做配图的前后对比点子。"),
       ('运营（每周复盘）',f"你是我的一人公司运营助理。下面是「{x['t']}」本周数据（访问、询价、付费、退款、渠道明细）：<粘贴数据>\n请：1) 对比 KPI 目标找出最大漏斗缺口；2) 给 3 个下周实验（各含假设、做法、成功指标）；3) 检查是否触发砍掉线：{x['k']}\n4) 列出可以写成脚本自动化的重复动作。输出用表格。")]
    ev=[dict(u=u,v=u.split('/')[2] not in UNVER) for u in x['ev']]
    out=dict(kind=KIND[k],cur=c,tiers=tiers,stream=stream,canvas=canvas,ue=ue,rev=rev,series={s:M[s]['rev'] for s in M},assume=assume,risks=risks,kills=kills,d7=d7,weeks=w,cal=cal,kpi=kpi,pipe=pipe,tools=tools,hrs=q['hrs'] if k!='svc' else q['hrs']+6,prompts=pr,ev=ev)
    if c=='¥':
        import json as J
        t=J.dumps(out,ensure_ascii=False)
        for a,b in [('收款 MoR（Creem / Lemon Squeezy / Paddle）','平台内收款（小红书店铺/面包多/爱发电/知识星球）'),('首选 MoR（Creem / Lemon Squeezy）代缴税；准备 Paddle 备用；首月小额测试提现','只走平台内交易或个体户/企业商户号；不用个人收款码做经营收款；不引导私下交易'),('接入 Creem/Lemon Squeezy 收款','开通平台店铺/面包多收款'),('Creem 或 Lemon Squeezy 托管结账','面包多/爱发电或已认证主体的微信支付'),('Creem / Lemon Squeezy','面包多 / 爱发电'),('域名 ~$12/年；托管 $0–20/月','域名 ~¥60/年；托管 ¥0–100/月（国内服务器需 ICP 备案）'),('工具订阅 ~$30/月；收款费 ~4–5%/单','工具订阅 ~¥200/月；平台抽成 5–20%/单')]:
            t=t.replace(a,b)
        out=J.loads(t)
    return out
