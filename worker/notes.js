// Idea Lab hotspot notes. GET /notes = all notes. POST /notes {id,status,note} needs header X-Pass (sha256 checked vs PASS_HASH secret).
// DELETE /notes?id=... also needs X-Pass.
const ORIGIN='https://siinxu.github.io';
const ST=['','interested','todo','done','ignore'];
function cors(req){const o=req.headers.get('Origin');return{'Access-Control-Allow-Origin':o===ORIGIN?ORIGIN:ORIGIN,'Access-Control-Allow-Methods':'GET,POST,DELETE,OPTIONS','Access-Control-Allow-Headers':'Content-Type,X-Pass','Vary':'Origin'}}
async function sha(s){const b=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s));return[...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,'0')).join('')}
function j(o,s,h){return new Response(JSON.stringify(o),{status:s||200,headers:{...h,'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'}})}
export default{async fetch(req,env){const h=cors(req),u=new URL(req.url);
if(req.method==='OPTIONS')return new Response(null,{headers:h});
if(u.pathname!=='/notes')return j({ok:true,service:'idea-lab-notes'},200,h);
if(req.method==='GET'){const v=await env.NOTES.get('all');return j(v?JSON.parse(v):{},200,h)}
const o=req.headers.get('Origin');if(o&&o!==ORIGIN)return j({error:'origin'},403,h);
if((await sha(req.headers.get('X-Pass')||''))!==env.PASS_HASH)return j({error:'auth'},401,h);
const all=JSON.parse(await env.NOTES.get('all')||'{}');
if(req.method==='DELETE'){const id=u.searchParams.get('id');delete all[id];await env.NOTES.put('all',JSON.stringify(all));return j({ok:true},200,h)}
if(req.method==='POST'){let b;try{b=await req.json()}catch(e){return j({error:'json'},400,h)}
const id=String(b.id||'').slice(0,120);if(!id)return j({error:'id'},400,h);
const status=ST.includes(b.status)?b.status:'';const note=String(b.note||'').slice(0,4000);
if(!status&&!note)delete all[id];else all[id]={status,note,updated:new Date().toISOString()};
await env.NOTES.put('all',JSON.stringify(all));return j({ok:true,item:all[id]||null},200,h)}
return j({error:'method'},405,h)}};
