"""Gera index.html (página pública) e admin123/index.html (edição) a partir de base.html.
Uso: python3 fonte/build.py   (rodar na raiz do repositório)
Não mexe em data.json."""
import json,os,re
AQUI=os.path.dirname(os.path.abspath(__file__))
RAIZ=os.path.dirname(AQUI)
SRC=open(os.path.join(AQUI,'base.html'),encoding='utf-8').read()
def build(ro):
    s=SRC
    def rep(a,b,cnt=1):
        nonlocal s
        assert a in s,(ro,a[:80]); s=s.replace(a,b,cnt)
    rep('<title>Agenda de Conteúdo</title>','<title>Agenda de Conteúdo</title>\n<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 32 32%27%3E%3Crect width=%2732%27 height=%2732%27 rx=%277%27 fill=%27%232F7FD6%27/%3E%3Crect x=%277%27 y=%279%27 width=%2718%27 height=%2716%27 rx=%273%27 fill=%27none%27 stroke=%27white%27 stroke-width=%272.5%27/%3E%3Cpath d=%27M7 14h18M12 6v5M20 6v5%27 stroke=%27white%27 stroke-width=%272.5%27 stroke-linecap=%27round%27/%3E%3C/svg%3E">')
    # flag
    rep('<script>\n','<script>\nconst READONLY='+('true' if ro else 'false')+';\nconst DATA_URL="'+('data.json' if ro else '../data.json')+'";\nif(READONLY)document.documentElement.classList.add("ro");\n')
    # css
    rep('/* Fila por canal */','''.ro .admin-only{display:none!important}
.pubcard ol{margin:0;padding-left:20px;display:flex;flex-direction:column;gap:6px;font-size:14px}
.pubcard p{margin:0;font-size:14px;color:var(--muted);max-width:70ch}
.pubcard a{color:var(--now)}
.pubrow{display:flex;gap:8px;flex-wrap:wrap}
.pubrow input{flex:1 1 260px;border:1px solid var(--line);background:var(--bg);border-radius:8px;padding:9px 10px;min-width:0;font:inherit}
.sync.warn i{background:var(--warn)} .sync.bad i{background:var(--bad)}
.item .date{font-family:var(--f-mono);font-size:11.5px;color:var(--muted);width:44px;line-height:1.2}

/* Fila por canal */''')
    # mark admin-only elements
    rep('<button type="button" class="bkb" id="exp">','<button type="button" class="bkb admin-only" id="exp">')
    rep('<label class="bkb" for="imp">','<label class="bkb admin-only" for="imp">')
    rep('<button type="button" class="ghost sm" id="mgOpen"','<button type="button" class="ghost sm admin-only" id="mgOpen"')
    rep('<section class="card mg" id="mg"','<section class="card mg admin-only" id="mg"')
    rep('<form class="card" id="form"','<form class="card admin-only" id="form"')
    if ro:
        rep('Clique num dia para ver e programar. Arraste um tema para outro dia para reagendar. Clique no nome de um canal para abrir o canal.','Clique num dia para ver o que está programado. Clique no nome de um canal para abrir o canal, ou no olho para mostrar ou esconder os temas dele.')
        rep('<title>Agenda de Conteúdo</title>','<title>Agenda de Conteúdo</title>\n<meta name="description" content="Programação dos canais Wealth Mind, Mentalista e Turma da Lili.">')
    else:
        rep('<title>Agenda de Conteúdo</title>','<title>Agenda de Conteúdo · Admin</title>')
        rep('<meta charset="utf-8">','<meta charset="utf-8">\n<meta name="robots" content="noindex,nofollow">')
        rep('<button type="button" class="bkb admin-only" id="exp">','<button type="button" class="bkb" id="pubBtn">Publicar agora</button><button type="button" class="bkb" id="useRemote" hidden>Usar a versão online</button><button type="button" class="bkb" id="ghBtn">Chave do GitHub</button><button type="button" class="bkb admin-only" id="exp">')
        rep('  <div class="qbar">','''  <section class="card pubcard" id="ghCard" hidden aria-label="Publicar para os amigos">
    <h2>Publicar para os amigos</h2>
    <p>Para suas mudanças aparecerem em canais.obunker.pro, esta página precisa de uma chave do GitHub. Você faz isso uma vez em cada aparelho onde for editar.</p>
    <ol>
      <li>Abra <a href="https://github.com/settings/personal-access-tokens/new" target="_blank" rel="noopener">github.com/settings/personal-access-tokens/new</a></li>
      <li>Em <b>Token name</b> escreva <b>agenda</b> e escolha uma validade em <b>Expiration</b>.</li>
      <li>Em <b>Repository access</b> marque <b>Only select repositories</b> e escolha <b>youtubeprojeto</b>.</li>
      <li>Em <b>Permissions</b> › <b>Repository permissions</b> › <b>Contents</b>, escolha <b>Read and write</b>.</li>
      <li>Clique em <b>Generate token</b>, copie a chave e cole aqui embaixo.</li>
    </ol>
    <div class="pubrow">
      <input type="password" id="ghTok" placeholder="github_pat_..." autocomplete="off">
      <button type="button" class="primary" id="ghSave" style="flex:0 0 auto;padding-inline:18px">Salvar chave</button>
      <button type="button" class="ghost" id="ghDel">Remover chave</button>
    </div>
    <p class="err" id="ghErr" hidden></p>
  </section>

  <div class="qbar">''')
    # item rows
    rep('Nada programado para este dia. Preencha o formulário acima para adicionar um tema.','${READONLY?"Nada programado para este dia.":"Nada programado para este dia. Preencha o formulário acima para adicionar um tema."}')
    # drag
    rep('el.draggable=true;','el.draggable=!READONLY;if(READONLY)el.style.cursor="default";')
    rep('cell.addEventListener("dragover",e=>{e.preventDefault();','cell.addEventListener("dragover",e=>{if(READONLY)return;e.preventDefault();')
    rep('cell.addEventListener("drop",async e=>{','cell.addEventListener("drop",async e=>{if(READONLY)return;')
    # remove old boot IIFE
    a=s.index('(async()=>{\n  let db=null;'); b=s.index('})();',a)+5
    s=s[:a]+s[b:]
    # storage + publish
    if ro:
        rep('function saveLocal(){try{localStorage.setItem("agenda.posts",JSON.stringify(posts))}catch(e){}}','function saveLocal(){}')
        rep('function saveLocalCh(){try{localStorage.setItem("agenda.canais",JSON.stringify(chans))}catch(e){}}','function saveLocalCh(){}')
        boot='''/* ---------- Carregar agenda publicada ---------- */
function setSync(t,cls){const s=$("sync");s.className="sync"+(cls?" "+cls:"");s.querySelector("span").textContent=t}
async function boot(first){
  try{
    const r=await fetch(DATA_URL+"?t="+Date.now(),{cache:"no-store"});
    if(!r.ok)throw 0;
    const j=await r.json();
    posts=Array.isArray(j.posts)?j.posts:[];chans=Array.isArray(j.canais)?j.canais:[];
    buildCH();render();
    const at=j.atualizado?new Date(j.atualizado):null;
    setSync(at?`Atualizado ${at.toLocaleDateString("pt-BR",{day:"2-digit",month:"2-digit"})} às ${at.toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"})}`:"Atualizado","on");
  }catch(e){if(first){chans=[];posts=[];buildCH();render()}setSync("Não foi possível carregar a agenda. Atualize a página.","bad")}
}
local=true;
$("data").value=sel;
boot(true);
setInterval(()=>{if(!document.hidden)boot(false)},120000);'''
    else:
        rep('function saveLocal(){try{localStorage.setItem("agenda.posts",JSON.stringify(posts))}catch(e){}}',
            'function persist(){try{localStorage.setItem("agenda.posts",JSON.stringify(posts));localStorage.setItem("agenda.canais",JSON.stringify(chans))}catch(e){}}\nfunction saveLocal(){persist();markDirty()}')
        rep('function saveLocalCh(){try{localStorage.setItem("agenda.canais",JSON.stringify(chans))}catch(e){}}','function saveLocalCh(){persist();markDirty()}')
        boot='''/* ---------- Publicação no GitHub ---------- */
const GH={owner:"brunoabreubr121314",repo:"youtubeprojeto",path:"data.json",branch:"main"};
const API=`https://api.github.com/repos/${GH.owner}/${GH.repo}/contents/${GH.path}`;
function tok(){try{return localStorage.getItem("agenda.ghtoken")||""}catch(e){return ""}}
function ls(k,v){try{if(v===undefined)return localStorage.getItem(k);if(v===null)localStorage.removeItem(k);else localStorage.setItem(k,v)}catch(e){return null}}
function isDirty(){return ls("agenda.dirty")==="1"}
function setDirty(v){ls("agenda.dirty",v?"1":"0")}
function getBase(){return ls("agenda.baseSha")||null}
function setBase(s){ls("agenda.baseSha",s||null)}
let pubTimer=null,publishing=false,pubAgain=false,pubErr="",lastPub=null,conflict=false;
function setSync(t,cls){const s=$("sync");s.className="sync"+(cls?" "+cls:"");s.querySelector("span").textContent=t}
function hdr(){return {Authorization:"Bearer "+tok(),Accept:"application/vnd.github+json"}}
function decode(b64){return JSON.parse(decodeURIComponent(escape(atob(b64.replace(/\\s/g,"")))))}
async function fetchRemote(){
  if(tok()){
    const r=await fetch(API+"?ref="+GH.branch+"&t="+Date.now(),{headers:hdr(),cache:"no-store"});
    if(r.status===401||r.status===403)throw {code:r.status};
    if(r.status===404)return {sha:null,data:null};
    if(!r.ok)throw {code:r.status};
    const j=await r.json();return {sha:j.sha,data:decode(j.content)};
  }
  const r=await fetch(DATA_URL+"?t="+Date.now(),{cache:"no-store"});
  return {sha:null,data:r.ok?await r.json():null};
}
function applyRemote(rem){
  const d=rem.data;if(!d||!Array.isArray(d.posts))return false;
  posts=d.posts;chans=Array.isArray(d.canais)&&d.canais.length?d.canais:DEFAULT_CH.map(c=>({...c}));
  persist();setDirty(false);if(rem.sha)setBase(rem.sha);conflict=false;pubErr="";
  buildCH();if(!CH[canal])canal=ORDER[0]||null;render();return true;
}
function updPub(){
  $("pubBtn").hidden=!tok()||(!isDirty()&&!conflict)||publishing;
  $("pubBtn").textContent=conflict?"Publicar a versão deste aparelho":"Publicar agora";
  $("useRemote").hidden=!conflict;
  $("ghBtn").textContent=tok()?"Chave do GitHub":"Conectar GitHub";
  if(publishing)return setSync("Publicando…","warn");
  if(conflict)return setSync("A agenda foi alterada em outra aba ou aparelho. Escolha qual versão manter","bad");
  if(pubErr)return setSync(pubErr,"bad");
  if(!tok())return setSync("Salvo só neste aparelho. Conecte o GitHub para publicar","warn");
  if(isDirty())return setSync("Alterações ainda não publicadas","warn");
  setSync(lastPub?`Publicado às ${lastPub.toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"})}`:"Publicado","on");
}
function markDirty(){setDirty(true);pubErr="";updPub();clearTimeout(pubTimer);if(tok()&&!conflict)pubTimer=setTimeout(publish,2000)}
async function publish(force){
  clearTimeout(pubTimer);
  if(!tok()){updPub();return}
  if(publishing){pubAgain=true;return}
  publishing=true;pubErr="";updPub();
  try{
    const g=await fetch(API+"?ref="+GH.branch+"&t="+Date.now(),{headers:hdr(),cache:"no-store"});
    if(g.status===401||g.status===403)throw {code:g.status};
    const sha=g.ok?(await g.json()).sha:undefined;
    const base=getBase();
    if(force!==true&&sha&&base&&sha!==base){conflict=true;publishing=false;updPub();return}
    const body=JSON.stringify({canais:chans,posts,atualizado:new Date().toISOString()},null,2);
    const content=btoa(unescape(encodeURIComponent(body)));
    const p=await fetch(API,{method:"PUT",headers:{...hdr(),"Content-Type":"application/json"},body:JSON.stringify({message:"Atualiza agenda",content,sha,branch:GH.branch})});
    if(p.status===409){conflict=true;publishing=false;updPub();return}
    if(!p.ok)throw {code:p.status};
    const pj=await p.json();setBase(pj.content&&pj.content.sha);
    setDirty(false);conflict=false;lastPub=new Date();
  }catch(e){
    const auth=e&&(e.code===401||e.code===403||e.code===404);
    pubErr=auth?"Chave do GitHub inválida ou sem permissão de escrita":"Não foi possível publicar. Tentando de novo…";
    if(!auth)pubTimer=setTimeout(publish,15000);
  }
  publishing=false;updPub();
  if(pubAgain){pubAgain=false;publish()}
}
$("pubBtn").onclick=()=>publish(conflict?true:undefined);
$("useRemote").onclick=async()=>{
  try{const rem=await fetchRemote();if(applyRemote(rem))toast("Versão online carregada");else toast("Não encontrei a versão online")}
  catch(e){toast("Não foi possível carregar a versão online")}
  updPub();
};
$("ghBtn").onclick=()=>{const c=$("ghCard");c.hidden=!c.hidden;if(!c.hidden){$("ghTok").value="";$("ghErr").hidden=true;$("ghTok").focus()}};
$("ghSave").onclick=async()=>{
  const t=$("ghTok").value.trim();const err=$("ghErr");
  if(!t){err.textContent="Cole a chave antes de salvar.";err.hidden=false;return}
  $("ghSave").disabled=true;err.hidden=true;
  try{
    const r=await fetch(`https://api.github.com/repos/${GH.owner}/${GH.repo}`,{headers:{Authorization:"Bearer "+t,Accept:"application/vnd.github+json"}});
    const j=r.ok?await r.json():null;
    if(!j||!j.permissions||!j.permissions.push)throw 0;
    ls("agenda.ghtoken",t);
    $("ghTok").value="";$("ghCard").hidden=true;toast("Chave salva");
    const rem=await fetchRemote();
    if(isDirty()&&getBase()&&rem.sha&&rem.sha!==getBase()){conflict=true;updPub()}
    else if(isDirty()){if(rem.sha&&!getBase())setBase(rem.sha);publish()}
    else{applyRemote(rem);updPub()}
  }catch(e){err.textContent="Essa chave não funcionou. Confira se ela tem acesso ao youtubeprojeto com Contents em Read and write.";err.hidden=false}
  finally{$("ghSave").disabled=false}
};
$("ghDel").onclick=()=>{ls("agenda.ghtoken",null);pubErr="";conflict=false;$("ghCard").hidden=true;updPub();toast("Chave removida deste aparelho")};

async function refreshIfChanged(){
  if(!tok()||publishing||isDirty()||conflict)return;
  try{const rem=await fetchRemote();if(rem.sha&&rem.sha!==getBase()&&!isDirty()){applyRemote(rem);updPub();toast("Agenda atualizada com mudanças de outro aparelho")}}catch(e){}
}
document.addEventListener("visibilitychange",()=>{if(!document.hidden)refreshIfChanged()});

async function boot(){
  local=true;
  let lp=null,lc=null;try{lp=JSON.parse(ls("agenda.posts")||"null");lc=JSON.parse(ls("agenda.canais")||"null")}catch(e){}
  let rem=null;try{rem=await fetchRemote()}catch(e){if(e&&(e.code===401||e.code===403))pubErr="Chave do GitHub inválida ou sem permissão de escrita"}
  if(isDirty()&&Array.isArray(lp)){
    posts=lp;if(Array.isArray(lc)&&lc.length)chans=lc;buildCH();render();
    if(rem&&rem.sha&&getBase()&&rem.sha!==getBase())conflict=true;
    else{if(rem&&rem.sha&&!getBase())setBase(rem.sha);if(tok())publish()}
  }else if(rem&&rem.data&&applyRemote(rem)){}
  else{if(Array.isArray(lp)){posts=lp;if(Array.isArray(lc)&&lc.length)chans=lc}buildCH();render()}
  updPub();
}
$("data").value=sel;
boot();'''
    rep('buildCH();\n$("data").value=sel;\nrender();',boot)
    # remove seeds
    s=re.sub(r'const SEED_POSTS=.*?;\nconst SEED_CH=.*?;\n','',s,count=1,flags=re.S)
    return s

os.makedirs(os.path.join(RAIZ,'admin123'),exist_ok=True)
open(os.path.join(RAIZ,'index.html'),'w',encoding='utf-8').write(build(True))
open(os.path.join(RAIZ,'admin123','index.html'),'w',encoding='utf-8').write(build(False))
print('Gerados: index.html e admin123/index.html')
