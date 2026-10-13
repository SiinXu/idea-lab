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
function render(){document.documentElement.lang=L;$('#lang').value=L;document.querySelectorAll('[data-i]').forEach(e=>e.textContent=t(e.dataset.i));
$('#upd').textContent=sh(H.lastUpdated)+' '+t('tz')+' (UTC+8) · '+H.items.length+' '+t('items');
$('#filt').innerHTML=['all','none',...ST].map(k=>`<button class="pill ${F==k?'on':''}" data-f="${k}">${t(k)}</button>`).join('');
$('#filt').querySelectorAll('button').forEach(b=>b.onclick=()=>{F=b.dataset.f;render()});
const its=[...H.items].sort((a,b)=>b.firstSeen.localeCompare(a.firstSeen)).filter(x=>{const s=(notes[x.id]||{}).status||'';return F=='all'||(F=='none'?!s:s==F)});
const g={};its.forEach(x=>(g[sh(x.firstSeen,1)]=g[sh(x.firstSeen,1)]||[]).push(x));
const fresh=Date.now()-new Date(H.lastUpdated)<36e5*3;
$('#days').innerHTML=Object.entries(g).map(([d,xs])=>`<section class="day"><h2>${d} · ${xs.length}</h2>${xs.map(x=>{const n=notes[x.id]||{};return`<article class="hi ${n.status=='ignore'?'ig':''}" id="h-${x.id}">
<h3>${esc(c(x.t))}</h3><p>${esc(c(x.s))}</p><div class="meta">${fresh&&x.firstSeen==H.lastUpdated?`<span class="nw">${t('new')}</span>`:''}<span>${t('first')} ${sh(x.firstSeen)} (UTC+8)</span>${x.links.map((l,i)=>`<a href="${esc(l)}" target="_blank" rel="noopener">${t('src')}${x.links.length>1?' '+(i+1):''} ↗</a>`).join('')}</div>
<div class="ed"><select class="pill">${['',...ST].map(s=>`<option value="${s}" ${n.status==s?'selected':''}>${t(s||'none')}</option>`).join('')}</select><button class="btn" data-s="${x.id}">${t('save')}</button><span class="s">${n.updated?sh(n.updated):''}</span><textarea placeholder="${esc(t('note'))}">${esc(n.note)}</textarea></div></article>`}).join('')}</section>`).join('');
document.querySelectorAll('[data-s]').forEach(b=>b.onclick=()=>save(b.dataset.s));auth()}
render();load();setInterval(()=>{if(!document.querySelector("textarea:focus"))location.reload()},15*60e3);
