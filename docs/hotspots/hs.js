const H=window.HS,$=s=>document.querySelector(s),W='https://idea-lab-notes.sinxu-xsy.workers.dev/notes';
const LANGS={"zh-Hans":"简体中文","zh-Hant":"繁體中文",en:"English",ja:"日本語",ko:"한국어",ms:"Bahasa Melayu",vi:"Tiếng Việt",fr:"Français",es:"Español",de:"Deutsch"};
const pick=()=>{const s=localStorage.lab_lang;if(s&&LANGS[s])return s;const n=(navigator.language||'en').toLowerCase();const tz=Intl.DateTimeFormat().resolvedOptions().timeZone||'';
if(n.startsWith('zh'))return /tw|hk|hant|mo/.test(n)?'zh-Hant':'zh-Hans';for(const l of['ja','ko','ms','vi','fr','es','de'])if(n.startsWith(l))return l;
if(/Shanghai|Chongqing/.test(tz))return'zh-Hans';if(/Taipei|Hong_Kong/.test(tz))return'zh-Hant';if(/Kuala_Lumpur/.test(tz))return'ms';return'en'};
let L=pick(),F='all',notes=JSON.parse(localStorage.hs_notes||'{}');
const t=k=>(H.ui[k]||{})[L]||(H.ui[k]||{}).en||k,c=o=>o[L]||o.en||o['zh-Hans']||'';
const esc=s=>String(s||'').replace(/[&<>"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));
const sh=(iso,d)=>{const x=new Date(iso);const o={timeZone:'Asia/Shanghai',hour12:false};return d?x.toLocaleDateString('sv-SE',o):x.toLocaleString('sv-SE',o).slice(0,16)};
document.documentElement.dataset.theme=localStorage.lab_theme||(matchMedia('(prefers-color-scheme: light)').matches?'light':'dark');
$('#theme').onclick=()=>{const v=document.documentElement.dataset.theme=='dark'?'light':'dark';document.documentElement.dataset.theme=v;localStorage.lab_theme=v};
for(const l in LANGS)$('#lang').add(new Option(LANGS[l],l));$('#lang').onchange=e=>{L=e.target.value;localStorage.lab_lang=L;render()};
const ST=['interested','todo','done','ignore'];
async function load(){try{const r=await fetch(W,{cache:'no-store'});const s=await r.json();notes={...notes,...s};for(const k in notes)if(!(k in s)&&!notes[k].local)delete notes[k];localStorage.hs_notes=JSON.stringify(notes)}catch(e){}render()}
async function save(id){const card=document.getElementById('h-'+id),status=card.querySelector('select').value,note=card.querySelector('textarea').value,msg=card.querySelector('.s');
const p=localStorage.hs_pass;notes[id]={status,note,updated:new Date().toISOString(),local:!p};localStorage.hs_notes=JSON.stringify(notes);
if(!p){msg.textContent=t('local');return}
try{const r=await fetch(W,{method:'POST',headers:{'Content-Type':'application/json','X-Pass':p},body:JSON.stringify({id,status,note})});if(!r.ok)throw r.status;delete notes[id].local;localStorage.hs_notes=JSON.stringify(notes);msg.textContent='✓ '+t('saved')}
catch(e){msg.textContent=t('err')+(e==401?' (401)':'')}}
function auth(){const a=$('#auth');if(localStorage.hs_pass){a.innerHTML=`<span>☁︎ ${t('saved')}</span><button class="pill" id="lo">${t('lock')}</button>`;$('#lo').onclick=()=>{delete localStorage.hs_pass;auth()}}
else{a.innerHTML=`<input type="password" id="pw" placeholder="${esc(t('pass'))}"><button class="btn" id="ul">${t('unlock')}</button>`;$('#ul').onclick=()=>{const v=$('#pw').value.trim();if(v){localStorage.hs_pass=v;auth();for(const k in notes)if(notes[k].local)fetch(W,{method:'POST',headers:{'Content-Type':'application/json','X-Pass':v},body:JSON.stringify({id:k,status:notes[k].status,note:notes[k].note})})}}}}
const X10={mark:{"zh-Hans":"标记 / 备注","zh-Hant":"標記 / 備註",en:"Mark / note",ja:"マーク / メモ",ko:"표시 / 메모",ms:"Tanda / nota",vi:"Đánh dấu / ghi chú",fr:"Marquer / note",es:"Marcar / nota",de:"Markieren / Notiz"},
q:{"zh-Hans":"搜索标题、摘要、来源…","zh-Hant":"搜尋標題、摘要、來源…",en:"Search titles, summaries, sources…",ja:"タイトル・要約・出典を検索…",ko:"제목, 요약, 출처 검색…",ms:"Cari tajuk, ringkasan, sumber…",vi:"Tìm tiêu đề, tóm tắt, nguồn…",fr:"Rechercher titres, résumés, sources…",es:"Buscar títulos, resúmenes, fuentes…",de:"Titel, Zusammenfassungen, Quellen suchen…"},
prev:{"zh-Hans":"上一页","zh-Hant":"上一頁",en:"Previous",ja:"前へ",ko:"이전",ms:"Sebelum",vi:"Trước",fr:"Précédent",es:"Anterior",de:"Zurück"},
next:{"zh-Hans":"下一页","zh-Hant":"下一頁",en:"Next",ja:"次へ",ko:"다음",ms:"Seterusnya",vi:"Sau",fr:"Suivant",es:"Siguiente",de:"Weiter"},
pg:{"zh-Hans":"第 {a} / {b} 页","zh-Hant":"第 {a} / {b} 頁",en:"Page {a} of {b}",ja:"{a} / {b} ページ",ko:"{a} / {b} 페이지",ms:"Halaman {a} / {b}",vi:"Trang {a} / {b}",fr:"Page {a} sur {b}",es:"Página {a} de {b}",de:"Seite {a} von {b}"},
r1:{"zh-Hans":"今天","zh-Hant":"今天",en:"Today",ja:"今日",ko:"오늘",ms:"Hari ini",vi:"Hôm nay",fr:"Aujourd’hui",es:"Hoy",de:"Heute"},
r7:{"zh-Hans":"近 7 天","zh-Hant":"近 7 天",en:"Last 7 days",ja:"過去7日",ko:"최근 7일",ms:"7 hari lepas",vi:"7 ngày qua",fr:"7 derniers jours",es:"Últimos 7 días",de:"Letzte 7 Tage"},
ra:{"zh-Hans":"全部时间","zh-Hant":"全部時間",en:"All time",ja:"全期間",ko:"전체 기간",ms:"Sepanjang masa",vi:"Mọi lúc",fr:"Tout",es:"Todo",de:"Gesamt"},
nores:{"zh-Hans":"没有匹配的条目","zh-Hant":"沒有符合的條目",en:"No matching items",ja:"該当なし",ko:"일치하는 항목 없음",ms:"Tiada item sepadan",vi:"Không có mục phù hợp",fr:"Aucun élément",es:"Sin resultados",de:"Keine Treffer"}};
const x10=(k,o)=>{let v=(X10[k]||{})[L]||(X10[k]||{}).en||k;for(const a in o||{})v=v.replace('{'+a+'}',o[a]);return v};
const PER=48;let Q='',RG='all',PG=1,OPEN=new Set();
try{const h=new URLSearchParams(location.hash.slice(1));PG=+h.get('p')||1;RG=h.get('r')||'all';F=h.get('f')||'all';Q=h.get('q')||''}catch(e){}
const host=u=>{try{return new URL(u).hostname.replace(/^www\./,'')}catch(e){return ''}};
function shell(){if($('#hsq'))return;const b=document.createElement('div');b.className='ctl';b.innerHTML=`<input id="hsq" type="search" autocomplete="off"><div class="filt" id="rng"></div>`;$('#filt').parentNode.insertAdjacentElement('afterend',b);
$('#hsq').value=Q;$('#hsq').oninput=e=>{Q=e.target.value;PG=1;render()};const pt=document.createElement('nav');pt.className='pgn';pt.id='pgt';$('#days').before(pt);const pb=document.createElement('nav');pb.className='pgn';pb.id='pgb';$('#days').after(pb)}
function render(){shell();document.documentElement.lang=L;$('#lang').value=L;document.querySelectorAll('[data-i]').forEach(e=>e.textContent=t(e.dataset.i));
$('#upd').textContent=sh(H.lastUpdated)+' '+t('tz')+' (UTC+8) · '+H.items.length+' '+t('items');$('#hsq').placeholder=x10('q');
const now=Date.now(),inR=x=>RG=='all'||(RG=='1'?sh(x.firstSeen,1)==sh(new Date().toISOString(),1):now-new Date(x.firstSeen)<7*864e5);
const ql=Q.trim().toLowerCase().split(/\s+/).filter(Boolean),inQ=x=>!ql.length||ql.every(w=>(c(x.t)+' '+c(x.s)+' '+x.title+' '+x.summary+' '+x.links.join(' ')).toLowerCase().includes(w));
const stOf=x=>(notes[x.id]||{}).status||'',base=H.items.filter(x=>inR(x)&&inQ(x));
const cnt=k=>base.filter(x=>{const s=stOf(x);return k=='all'||(k=='none'?!s:s==k)}).length;
$('#filt').innerHTML=['all','none',...ST].map(k=>{const n=cnt(k);return n||k=='all'||F==k?`<button class="pill ${F==k?'on':''}" data-f="${k}">${t(k)} <small>${n}</small></button>`:''}).join('');
$('#filt').querySelectorAll('button').forEach(b=>b.onclick=()=>{F=b.dataset.f;PG=1;render()});
$('#rng').innerHTML=[['1','r1'],['7','r7'],['all','ra']].map(([k,l])=>`<button class="pill ${RG==k?'on':''}" data-r="${k}">${x10(l)}</button>`).join('');
$('#rng').querySelectorAll('button').forEach(b=>b.onclick=()=>{RG=b.dataset.r;PG=1;render()});
const its=base.sort((a,b)=>b.firstSeen.localeCompare(a.firstSeen)).filter(x=>{const s=stOf(x);return F=='all'||(F=='none'?!s:s==F)});
const NP=Math.max(1,Math.ceil(its.length/PER));PG=Math.min(Math.max(1,PG),NP);const pg=its.slice((PG-1)*PER,PG*PER);
const nav=NP>1?`<button class="pill" data-p="${PG-1}" ${PG<=1?'disabled':''}>← ${x10('prev')}</button><span class="mono">${x10('pg',{a:PG,b:NP})} · ${its.length} ${t('items')}</span><button class="pill" data-p="${PG+1}" ${PG>=NP?'disabled':''}>${x10('next')} →</button>`:`<span class="mono">${its.length} ${t('items')}</span>`;
$('#pgt').innerHTML=nav;$('#pgb').innerHTML=NP>1?nav:'';
document.querySelectorAll('.pgn [data-p]').forEach(b=>b.onclick=()=>{PG=+b.dataset.p;render();$('#pgt').scrollIntoView({block:'start'})});
try{history.replaceState(null,'','#'+new URLSearchParams({p:PG,r:RG,f:F,q:Q}).toString())}catch(e){}
const g={};pg.forEach(x=>(g[sh(x.firstSeen,1)]=g[sh(x.firstSeen,1)]||[]).push(x));
const fresh=Date.now()-new Date(H.lastUpdated)<36e5*3;
$('#days').innerHTML=pg.length?Object.entries(g).map(([d,xs])=>`<section class="day"><h2>${d} · ${xs.length}</h2>${xs.map(x=>{const n=notes[x.id]||{},op=OPEN.has(x.id);return`<article class="hi ${n.status=='ignore'?'ig':''}" id="h-${x.id}">
<h3>${esc(c(x.t))}</h3><p>${esc(c(x.s))}</p><div class="meta">${fresh&&x.firstSeen==H.lastUpdated?`<span class="nw">${t('new')}</span>`:''}${n.status?`<span class="sbg s-${n.status}">${t(n.status)}</span>`:''}<span>${sh(x.firstSeen).slice(11)} (UTC+8)</span>${x.links.map(l=>`<a href="${esc(l)}" target="_blank" rel="noopener">${esc(host(l)||t('src'))} ↗</a>`).join('')}<button class="mk" data-o="${x.id}" aria-expanded="${op}">${x10('mark')}</button></div>
${n.note&&!op?`<p class="nt">✎ ${esc(n.note)}</p>`:''}<div class="ed" ${op?'':'hidden'}><select class="pill">${['',...ST].map(s=>`<option value="${s}" ${n.status==s?'selected':''}>${t(s||'none')}</option>`).join('')}</select><button class="btn" data-s="${x.id}">${t('save')}</button><span class="s">${n.updated?sh(n.updated):''}</span><textarea placeholder="${esc(t('note'))}">${esc(n.note)}</textarea></div></article>`}).join('')}</section>`).join(''):`<p class="empty mono">${x10('nores')}</p>`;
document.querySelectorAll('[data-s]').forEach(b=>b.onclick=()=>save(b.dataset.s));
document.querySelectorAll('[data-o]').forEach(b=>b.onclick=()=>{const id=b.dataset.o;OPEN.has(id)?OPEN.delete(id):OPEN.add(id);const a=document.getElementById('h-'+id),e=a.querySelector('.ed'),nt=a.querySelector('.nt');e.hidden=!OPEN.has(id);b.setAttribute('aria-expanded',OPEN.has(id));if(nt)nt.hidden=OPEN.has(id);if(OPEN.has(id))e.querySelector('select').focus()});auth()}
render();load();setInterval(()=>{if(!document.querySelector("textarea:focus"))location.reload()},15*60e3);
