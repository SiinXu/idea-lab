const D=window.DATA,$=s=>document.querySelector(s);
const pick=()=>{const s=localStorage.lab_lang;if(s&&UI[s])return s;const n=(navigator.language||'en').toLowerCase();const tz=Intl.DateTimeFormat().resolvedOptions().timeZone||'';
if(n.startsWith('zh'))return /tw|hk|hant|mo/.test(n)?'zh-Hant':'zh-Hans';for(const l of['ja','ko','ms','vi','fr','es','de'])if(n.startsWith(l))return l;
if(/Shanghai|Chongqing/.test(tz))return'zh-Hans';if(/Taipei|Hong_Kong/.test(tz))return'zh-Hant';if(/Kuala_Lumpur/.test(tz))return'ms';return'en'};
let L=pick(),fav=new Set(JSON.parse(localStorage.lab_fav||'[]')),tagF='',favOnly=false;
const t=k=>UI[L][k],c=o=>o[L]||o.en;
document.documentElement.dataset.theme=localStorage.lab_theme||(matchMedia('(prefers-color-scheme: light)').matches?'light':'dark');
$('#theme').onclick=()=>{const v=document.documentElement.dataset.theme=='dark'?'light':'dark';document.documentElement.dataset.theme=v;localStorage.lab_theme=v};
for(const l in LANGS)$('#lang').add(new Option(LANGS[l],l));$('#lang').onchange=e=>{L=e.target.value;localStorage.lab_lang=L;render()};
const score=i=>i.s.reduce((a,b)=>a+b,0)*5;
function card(i,n){const f=fav.has(i.id);return`<article class="card" data-id="${i.id}" style="animation-delay:${n*40}ms"><div class="ci">
<div class="row"><span class="tag">${c(i.tag)}</span><span class="mono" style="font-size:12px;color:var(--mut)">${t('sc')} ${score(i)}</span><button class="fav ${f?'on':''}" data-f="${i.id}">${f?'★':'☆'}</button></div>
<h3>${c(i.t)}</h3><p>${c(i.p)}</p><div class="kv"><b>${t('money')}</b> · ${c(i.mo)}</div>
<a class="more" href="idea/${i.id}/">${t('full')}</a><div class="bars">${['speed','cheap','autoS','demand'].map((k,j)=>`<div class="bar">${t(k)}<i style="--w:${i.s[j]*20}%"></i></div>`).join('')}</div></div></article>`}
function render(){document.documentElement.lang=L;$('#lang').value=L;
document.querySelectorAll('[data-i]').forEach(e=>e.textContent=t(e.dataset.i));
$('#today').textContent=new Date().toLocaleDateString(L,{weekday:'long',year:'numeric',month:'long',day:'numeric'});
const vis=i=>(!tagF||c(i.tag)==tagF)&&(!favOnly||fav.has(i.id));
['green','today','week','evergreen'].forEach(s=>{const a=D.ideas.filter(i=>i.sec==s&&(s!='evergreen'||vis(i))&&(!favOnly||fav.has(i.id))).sort((a,b)=>score(b)-score(a));$('#g-'+s).innerHTML=a.map(card).join('')});
const tags=[...new Set(D.ideas.filter(i=>i.sec=='evergreen').map(i=>c(i.tag)))];
$('#chips').innerHTML=[`<button class="chip ${!tagF?'on':''}" data-t="">${t('all')}</button>`,...tags.map(g=>`<button class="chip ${tagF==g?'on':''}" data-t="${g}">${g}</button>`)].join('');
$('#g-pb').innerHTML=D.pb.map((p,n)=>`<div><div class="n">0${n+1}</div><h4>${c(p.t)}</h4><p>${c(p.d)}</p></div>`).join('');
$('#g-rk').innerHTML=D.rk.map(r=>`<li><div><b>${c(r.t)}</b><span>${c(r.d)}</span></div></li>`).join('');
$('[data-i=mt]').style.display=L=='zh-Hans'?'none':'';
tick('#nIdeas',D.ideas.length);tick('#nToday',D.ideas.filter(i=>i.sec=='today').length);tick('#nFav',fav.size);bind()}
function tick(s,v){const e=$(s),st=performance.now();const f=n=>{const p=Math.min(1,(n-st)/900);e.textContent=Math.round(v*(1-Math.pow(1-p,3)));if(p<1)requestAnimationFrame(f)};requestAnimationFrame(f)}
function bind(){document.querySelectorAll('.card').forEach(el=>{el.onmousemove=e=>{const r=el.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top;el.style.setProperty('--x',x+'px');el.style.setProperty('--y',y+'px');el.style.transform=`perspective(900px) rotateX(${(y/r.height-.5)*-5}deg) rotateY(${(x/r.width-.5)*5}deg)`};el.onmouseleave=()=>el.style.transform='';el.onclick=e=>{if(e.target.dataset.f||e.target.closest('a'))return;location.href='idea/'+el.dataset.id+'/'}});
document.querySelectorAll('[data-f]').forEach(b=>b.onclick=()=>{const id=b.dataset.f;fav.has(id)?fav.delete(id):fav.add(id);localStorage.lab_fav=JSON.stringify([...fav]);render()});
document.querySelectorAll('.chip').forEach(b=>b.onclick=()=>{tagF=b.dataset.t;render()})}
function open(id){const i=D.ideas.find(x=>x.id==id);const host=u=>new URL(u).hostname.replace('www.','');
$('#dlgIn').innerHTML=`<button class="x" onclick="dlg.close()">×</button><span class="tag">${c(i.tag)}</span><h3>${c(i.t)}</h3><dl>
${[['problem','p'],['who','w'],['mvp','m'],['money','mo'],['auto','au'],['risk','r'],['kill','k']].map(([a,b])=>`<dt>${t(a)}</dt><dd>${c(i[b])}</dd>`).join('')}
<dt>${t('ev')}</dt><dd>${i.ev.map(u=>`<a href="${u}" target="_blank" rel="noopener">↗ ${host(u)}</a>`).join('<br>')}</dd></dl>
<textarea placeholder="${t('note')}" id="nt">${localStorage['lab_n_'+id]||''}</textarea>`;
$('#nt').oninput=e=>localStorage['lab_n_'+id]=e.target.value;$('#dlg').showModal()}
$('#dlg').onclick=e=>{if(e.target.id=='dlg')$('#dlg').close()};
$('#spark').onclick=()=>{const a=D.ideas[Math.random()*D.ideas.length|0];let b;do b=D.ideas[Math.random()*D.ideas.length|0];while(b==a);
$('#sparkOut').innerHTML=`<div class="sp"><b>${t('combo')}</b> ${c(a.t)} <b>×</b> ${c(b.t)}<p style="color:var(--mut);margin:8px 0 0;font-size:14px">${t('who')}: ${c(a.w)}<br>${t('auto')}: ${c(b.au)}</p><button class="chip" style="margin-top:10px" onclick="location.href='idea/${a.id}/'">→ ${c(a.t)}</button></div>`};
$('#favOnly').onclick=e=>{e.preventDefault();favOnly=!favOnly;e.currentTarget.classList.toggle('on',favOnly);render()};
addEventListener('pointermove',e=>{const s=$('#spot');s.style.left=e.clientX+'px';s.style.top=e.clientY+'px'});
render();
