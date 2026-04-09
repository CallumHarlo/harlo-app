import { useState, useEffect, useCallback } from "react";
import { supabase } from "./supabase";

// ─── PASTE YOUR ANTHROPIC API KEY HERE ───
const ANTHROPIC_API_KEY = "YOUR_API_KEY_HERE";
// ─────────────────────────────────────────

const C = {
  roseDk:"#72243E",rose:"#C9637A",roseLt:"#FBEAF0",
  tealDk:"#085041",teal:"#1D9E75",tealLt:"#E1F5EE",
  amberDk:"#633806",amber:"#BA7517",amberLt:"#FAEEDA",
  purpleDk:"#3C3489",purple:"#7F77DD",purpleLt:"#EEEDFE",
  blueDk:"#0C447C",blue:"#378ADD",blueLt:"#E6F1FB",
  ink:"#2C2A28",mid:"#6b6760",paper:"#FAF8F5",
};

const css = `
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent;}
body{font-family:'Nunito',sans-serif;background:#111;display:flex;justify-content:center;min-height:100vh;}
#root{width:100%;max-width:390px;margin:0 auto;}
.phone{background:${C.paper};min-height:100vh;display:flex;flex-direction:column;}
.screen{flex:1;display:flex;flex-direction:column;animation:fi .3s ease;}
@keyframes fi{from{opacity:0;transform:translateX(10px)}to{opacity:1;transform:none}}
.hdr{padding:52px 20px 22px;}
.back{font-size:11px;color:rgba(255,255,255,.55);margin-bottom:12px;cursor:pointer;display:inline-block;}
.htitle{font-family:'Playfair Display',serif;font-size:22px;color:white;}
.hsub{font-size:11px;color:rgba(255,255,255,.5);margin-top:4px;}
.body{padding:14px 16px 100px;flex:1;overflow-y:auto;}
.nav{position:fixed;bottom:0;left:50%;transform:translateX(-50%);width:100%;max-width:390px;display:flex;background:white;border-top:.5px solid #e8e2da;padding:10px 0 24px;z-index:100;}
.ni{flex:1;display:flex;flex-direction:column;align-items:center;gap:3px;cursor:pointer;}
.ni-i{font-size:20px;}
.ni-l{font-size:9px;color:${C.mid};}
.ni.on .ni-l{color:${C.roseDk};font-weight:600;}
.ni-d{width:4px;height:4px;border-radius:50%;background:${C.rose};display:none;margin:0 auto;}
.ni.on .ni-d{display:block;}
input,textarea{font-family:'Nunito',sans-serif;outline:none;}
button{font-family:'Nunito',sans-serif;cursor:pointer;border:none;}
.card{background:white;border-radius:14px;border:.5px solid #e8e2da;padding:14px;margin-bottom:10px;}
.tag{padding:6px 12px;border-radius:20px;font-size:11px;font-weight:600;border:.5px solid #e0dbd4;color:${C.mid};cursor:pointer;background:white;transition:all .15s;display:inline-flex;align-items:center;gap:5px;}
.tag.rz{background:${C.roseLt};border-color:${C.rose};color:${C.roseDk};}
.tag.bz{background:${C.blueLt};border-color:${C.blue};color:${C.blueDk};}
.pbtn{background:${C.roseDk};color:white;border-radius:12px;padding:13px;width:100%;font-size:14px;font-weight:600;transition:opacity .15s;}
.pbtn:disabled{opacity:.5;cursor:not-allowed;}
.slbl{font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:${C.mid};margin-bottom:8px;}
.spin{width:18px;height:18px;border:2px solid rgba(255,255,255,.3);border-top-color:white;border-radius:50%;animation:sp .7s linear infinite;display:inline-block;vertical-align:middle;}
@keyframes sp{to{transform:rotate(360deg)}}
.td{width:6px;height:6px;border-radius:50%;background:${C.teal};animation:bo 1.2s infinite;display:inline-block;margin:0 2px;}
.td:nth-child(2){animation-delay:.2s}.td:nth-child(3){animation-delay:.4s}
@keyframes bo{0%,80%,100%{transform:scale(.6);opacity:.4}40%{transform:scale(1);opacity:1}}
.err{background:#FCEBEB;border:.5px solid #F09595;border-radius:10px;padding:10px 13px;font-size:12px;color:#A32D2D;margin-bottom:12px;}
.ok{background:${C.tealLt};border:.5px solid ${C.teal};border-radius:10px;padding:10px 13px;font-size:12px;color:${C.tealDk};margin-bottom:12px;}
.inp{width:100%;padding:12px 14px;border-radius:10px;border:.5px solid #e0dbd4;background:white;font-size:14px;color:${C.ink};margin-bottom:14px;}
.ta{width:100%;background:${C.paper};border:.5px solid #e0dbd4;border-radius:10px;padding:11px 13px;font-size:13px;color:${C.ink};resize:none;line-height:1.6;}
.tog{width:38px;height:22px;border-radius:11px;position:relative;cursor:pointer;transition:background .2s;}
.tog-k{width:18px;height:18px;border-radius:50%;background:white;position:absolute;top:2px;transition:left .2s;}
`;

async function getAI(text) {
  if (!ANTHROPIC_API_KEY || ANTHROPIC_API_KEY==="YOUR_API_KEY_HERE") {
    await new Promise(r=>setTimeout(r,1200));
    return "Thank you for sharing that. It takes real courage to put your feelings into words. Be gentle with yourself today — what you're feeling is valid.";
  }
  try {
    const r = await fetch("https://api.anthropic.com/v1/messages",{method:"POST",headers:{"Content-Type":"application/json","x-api-key":ANTHROPIC_API_KEY,"anthropic-version":"2023-06-01"},body:JSON.stringify({model:"claude-sonnet-4-20250514",max_tokens:200,system:"You are Better You, a warm compassionate mental wellness companion. Respond to journal entries with a short empathetic reflection (2-3 sentences). Don't give advice. Reflect what you hear with care, end with a gentle open question. Sound human and warm.",messages:[{role:"user",content:`Journal entry: "${text}"`}]})});
    const d = await r.json();
    return d.content?.[0]?.text||"Thank you for sharing. Your feelings matter.";
  } catch { return "Thank you for sharing that with me. Your feelings matter."; }
}

function Nav({active,go}) {
  return <nav className="nav">{[["🏠","home","home"],["✍️","write","entry"],["💬","reflect","reflect"],["⚙️","settings","reminders"]].map(([ic,k,sc])=>(
    <div key={k} className={`ni${active===k?" on":""}`} onClick={()=>go(sc)}>
      <span className="ni-i">{ic}</span><div className="ni-d"></div><span className="ni-l">{k}</span>
    </div>))}</nav>;
}

function Spinner({color}) { return <div className="spin" style={color?{borderTopColor:color}:{}}></div>; }

function Toggle({on,color,onChange}) {
  return <div className="tog" style={{background:on?color:"#d0cac2"}} onClick={onChange}><div className="tog-k" style={{left:on?18:2}}></div></div>;
}

// ── AUTH ──
function AuthScreen() {
  const [mode,setMode]=useState("login");
  const [email,setEmail]=useState("");
  const [pw,setPw]=useState("");
  const [name,setName]=useState("");
  const [load,setLoad]=useState(false);
  const [err,setErr]=useState("");
  const [ok,setOk]=useState("");

  const submit = async () => {
    if(!email.trim()||!pw.trim()){setErr("Please enter your email and password.");return;}
    setLoad(true);setErr("");setOk("");
    try {
      if(mode==="login"){
        const {error}=await supabase.auth.signInWithPassword({email:email.trim(),password:pw});
        if(error)setErr(error.message);
      } else {
        const displayName=name.trim()||email.split("@")[0];
        const {data,error}=await supabase.auth.signUp({email:email.trim(),password:pw,options:{data:{display_name:displayName}}});
        if(error){setErr(error.message);}
        else{setOk("Account created! Check your email for a confirmation link, then sign in.");setMode("login");}
      }
    } catch(e){setErr("Something went wrong. Please try again.");}
    setLoad(false);
  };

  return (
    <div className="screen" style={{background:C.roseDk}}>
      <div style={{flex:1,display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",padding:"40px 0 20px"}}>
        <div style={{fontFamily:"'Playfair Display',serif",fontSize:44,color:"white",fontWeight:600}}>Better <em style={{color:"#F4C0D1"}}>You</em></div>
        <div style={{fontSize:11,color:"rgba(255,255,255,.55)",letterSpacing:".1em",textTransform:"uppercase",marginTop:6}}>Be good to yourself</div>
      </div>
      <div style={{background:C.paper,borderRadius:"28px 28px 0 0",padding:"28px 24px 48px"}}>
        <div style={{display:"flex",background:"#eee9e2",borderRadius:10,padding:3,marginBottom:20}}>
          {[["login","Sign in"],["signup","Sign up"]].map(([m,l])=>(
            <button key={m} onClick={()=>{setMode(m);setErr("");setOk("");}} style={{flex:1,padding:"8px 0",fontSize:13,fontWeight:600,borderRadius:8,background:mode===m?"white":"transparent",color:mode===m?C.roseDk:C.mid,border:"none"}}>{l}</button>
          ))}
        </div>
        {err&&<div className="err">{err}</div>}
        {ok&&<div className="ok">{ok}</div>}
        {mode==="signup"&&<><div className="slbl">Your name (optional)</div><input className="inp" value={name} onChange={e=>setName(e.target.value)} placeholder="What should we call you?" /></>}
        <div className="slbl">Email</div>
        <input className="inp" type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="your@email.com" autoComplete="email" />
        <div className="slbl">Password</div>
        <input className="inp" type="password" value={pw} onChange={e=>setPw(e.target.value)} placeholder="at least 6 characters" style={{marginBottom:20}} />
        <button className="pbtn" onClick={submit} style={{opacity:load?0.7:1}} disabled={load}>
          {load?<><Spinner/>&nbsp;{mode==="login"?"Signing in...":"Creating account..."}</>:mode==="login"?"Sign in":"Create account"}
        </button>
      </div>
    </div>
  );
}

// ── HOME ──
function HomeScreen({go,user,cheers}) {
  const unread=cheers.filter(c=>!c.is_read).length;
  const hr=new Date().getHours();
  const greet=hr<12?"morning":hr<17?"afternoon":"evening";
  const name=user?.user_metadata?.display_name||user?.email?.split("@")[0]||"there";
  return (
    <div className="screen">
      <div className="hdr" style={{background:C.roseDk,paddingTop:56}}>
        <div style={{fontSize:11,color:"rgba(255,255,255,.55)"}}>Good {greet}</div>
        <div className="htitle">Hello, {name}</div>
        <div className="hsub">{new Date().toLocaleDateString("en-AU",{weekday:"long",month:"long",day:"numeric"})}</div>
      </div>
      <div className="body">
        {unread>0&&<div onClick={()=>go("cheers")} style={{background:C.roseLt,borderRadius:14,padding:"12px 14px",border:"0.5px solid #F4C0D1",marginBottom:12,cursor:"pointer"}}>
          <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:6}}>
            <div style={{fontSize:13,fontWeight:600,color:C.roseDk}}>✦ Cheers for you</div>
            <div style={{background:C.rose,color:"white",fontSize:10,fontWeight:700,padding:"2px 8px",borderRadius:20}}>{unread} new</div>
          </div>
          <div style={{fontSize:11,color:C.roseDk,fontStyle:"italic"}}>Tap to see messages from your supporters</div>
        </div>}
        {[
          {ic:"✍️",t:"New entry",s:"Write how you feel today",col:C.roseLt,sc:"entry"},
          {ic:"💬",t:"Reply & reflect",s:"AI responds to your entries",col:C.tealLt,sc:"reflect"},
          {ic:"📤",t:"Publish entry",s:"Share to your community",col:C.amberLt,sc:"share"},
          {ic:"✦",t:"Send a cheer",s:"Encourage someone you follow",col:C.roseLt,sc:"sendCheer"},
        ].map(c=>(
          <div key={c.sc} onClick={()=>go(c.sc)} className="card" style={{display:"flex",alignItems:"center",gap:12,cursor:"pointer"}}>
            <div style={{width:40,height:40,borderRadius:11,background:c.col,display:"flex",alignItems:"center",justifyContent:"center",fontSize:18,flexShrink:0}}>{c.ic}</div>
            <div style={{flex:1}}><div style={{fontSize:14,fontWeight:600,color:C.ink}}>{c.t}</div><div style={{fontSize:11,color:C.mid,marginTop:1}}>{c.s}</div></div>
            <div style={{color:"#c0b8ae",fontSize:18}}>›</div>
          </div>
        ))}
        <div style={{background:C.tealLt,borderRadius:12,padding:"10px 13px",display:"flex",alignItems:"center",gap:8,marginTop:4}}>
          <div style={{width:7,height:7,borderRadius:"50%",background:C.teal,flexShrink:0}}></div>
          <div style={{fontSize:11,color:C.tealDk,lineHeight:1.5}}>Reminder: take 5 minutes for yourself today.</div>
        </div>
        <div onClick={()=>supabase.auth.signOut()} style={{textAlign:"center",fontSize:11,color:C.mid,marginTop:20,cursor:"pointer",padding:"8px 0"}}>Sign out</div>
      </div>
      <Nav active="home" go={go}/>
    </div>
  );
}

// ── NEW ENTRY ──
function EntryScreen({go,user,onSave}) {
  const [text,setText]=useState("");
  const [tags,setTags]=useState([]);
  const [date,setDate]=useState(new Date().toISOString().split("T")[0]);
  const [saving,setSaving]=useState(false);
  const [err,setErr]=useState("");
  const allTags=[{l:"grateful",e:"🙂",s:"rz"},{l:"anxious",e:"😰",s:"rz"},{l:"calm",e:"😌",s:"rz"},{l:"sad",e:"😔",s:"bz"},{l:"hopeful",e:"🌱",s:"rz"},{l:"proud",e:"✨",s:"rz"}];
  const tog=(l)=>setTags(t=>t.includes(l)?t.filter(x=>x!==l):[...t,l]);

  const save = async () => {
    if(!text.trim())return;
    setSaving(true);setErr("");
    const ai=await getAI(text);
    const {error}=await supabase.from("entries").insert({user_id:user.id,entry_date:date,text:text.trim(),tags,ai_reply:ai,self_reply:""});
    if(error){setErr("Couldn't save. Try again.");setSaving(false);return;}
    onSave(); go("reflect");
  };

  return (
    <div className="screen">
      <div className="hdr" style={{background:C.roseDk}}>
        <div className="back" onClick={()=>go("home")}>← back</div>
        <div className="htitle">New entry</div>
      </div>
      <div className="body">
        {err&&<div className="err">{err}</div>}
        <div style={{display:"flex",gap:8,marginBottom:14}}>
          <div style={{flex:1,background:C.roseLt,borderRadius:10,padding:"9px 12px"}}>
            <div style={{fontSize:9,textTransform:"uppercase",letterSpacing:".06em",color:C.roseDk,marginBottom:3}}>Today</div>
            <div style={{fontSize:13,fontWeight:600,color:C.roseDk}}>{new Date().toLocaleDateString("en-AU",{month:"short",day:"numeric",year:"numeric"})}</div>
          </div>
          <div style={{flex:1,background:C.tealLt,borderRadius:10,padding:"9px 12px"}}>
            <div style={{fontSize:9,textTransform:"uppercase",letterSpacing:".06em",color:C.tealDk,marginBottom:3}}>Select date</div>
            <input type="date" value={date} onChange={e=>setDate(e.target.value)} style={{fontSize:11,fontWeight:600,color:C.tealDk,background:"transparent",border:"none",width:"100%",padding:0}}/>
          </div>
        </div>
        <textarea value={text} onChange={e=>setText(e.target.value)} placeholder="Today I felt..." className="ta" style={{minHeight:140,borderRadius:12,padding:"12px 14px",fontSize:14,marginBottom:14}}/>
        <div className="slbl">How are you feeling?</div>
        <div style={{display:"flex",flexWrap:"wrap",gap:6,marginBottom:16}}>
          {allTags.map(t=>(
            <button key={t.l} className={`tag${tags.includes(t.l)?" "+t.s:""}`} onClick={()=>tog(t.l)}>
              <span style={{fontSize:14}}>{t.e}</span>{t.l}
            </button>
          ))}
        </div>
        <button className="pbtn" onClick={save} disabled={saving||!text.trim()}>
          {saving?<><Spinner/>&nbsp;Saving & getting reflection...</>:"Save entry"}
        </button>
      </div>
      <Nav active="write" go={go}/>
    </div>
  );
}

// ── REFLECT ──
function ReflectScreen({go,user,rk}) {
  const [entries,setEntries]=useState([]);
  const [sel,setSel]=useState(0);
  const [sr,setSr]=useState("");
  const [ctab,setCtab]=useState("self");
  const [afu,setAfu]=useState("");
  const [loadAfu,setLoadAfu]=useState(false);
  const [loading,setLoading]=useState(true);

  useEffect(()=>{
    (async()=>{
      setLoading(true);
      const {data}=await supabase.from("entries").select("*").eq("user_id",user.id).order("entry_date",{ascending:false}).limit(10);
      setEntries(data||[]);setLoading(false);
    })();
  },[user.id,rk]);

  const fmt=d=>new Date(d+"T00:00:00").toLocaleDateString("en-AU",{month:"short",day:"numeric"});
  const e=entries[sel];

  const saveSr=async()=>{
    await supabase.from("entries").update({self_reply:sr}).eq("id",e.id);
    setEntries(en=>en.map((x,i)=>i===sel?{...x,self_reply:sr}:x));setSr("");
  };
  const sendAfu=async()=>{
    if(!afu.trim())return;
    setLoadAfu(true);
    const r=await getAI(`Original: "${e.text}". Follow-up: "${afu}"`);
    await supabase.from("entries").update({ai_reply:r}).eq("id",e.id);
    setEntries(en=>en.map((x,i)=>i===sel?{...x,ai_reply:r}:x));
    setAfu("");setLoadAfu(false);
  };

  if(loading) return <div style={{display:"flex",alignItems:"center",justifyContent:"center",minHeight:"60vh"}}><Spinner color={C.teal}/></div>;

  return (
    <div className="screen">
      <div className="hdr" style={{background:C.tealDk}}>
        <div className="back" onClick={()=>go("home")}>← home</div>
        <div className="htitle">Reply & reflect</div>
        <div className="hsub">A conversation with yourself</div>
      </div>
      <div className="body">
        {entries.length===0?(
          <div className="card" style={{textAlign:"center",padding:"32px 20px"}}>
            <div style={{fontSize:32,marginBottom:12}}>✍️</div>
            <div style={{fontSize:14,fontWeight:600,color:C.ink,marginBottom:6}}>No entries yet</div>
            <div style={{fontSize:12,color:C.mid,marginBottom:16}}>Write your first entry to get a reflection.</div>
            <button className="pbtn" onClick={()=>go("entry")}>Write first entry</button>
          </div>
        ):(
          <>
            <div style={{display:"flex",gap:6,marginBottom:14,background:"#eee9e2",borderRadius:10,padding:3,overflowX:"auto"}}>
              {entries.slice(0,4).map((en,i)=>(
                <button key={en.id} onClick={()=>setSel(i)} style={{flex:"0 0 auto",padding:"7px 12px",fontSize:11,fontWeight:600,borderRadius:8,background:sel===i?"white":"transparent",color:sel===i?C.tealDk:C.mid,border:"none",whiteSpace:"nowrap"}}>{fmt(en.entry_date)}</button>
              ))}
            </div>
            <div className="card" style={{marginBottom:8}}>
              <div style={{fontSize:9,textTransform:"uppercase",letterSpacing:".06em",color:C.mid,marginBottom:6}}>{fmt(e.entry_date)} · your entry</div>
              <div style={{fontSize:13,color:C.ink,lineHeight:1.7}}>"{e.text}"</div>
              {e.tags?.length>0&&<div style={{display:"flex",gap:5,flexWrap:"wrap",marginTop:8}}>{e.tags.map(t=><span key={t} className={`tag ${t==="sad"?"bz":"rz"}`} style={{fontSize:10,padding:"3px 9px"}}>{t}</span>)}</div>}
            </div>
            <div style={{background:C.tealLt,borderRadius:12,padding:"12px 14px",borderLeft:`3px solid ${C.teal}`,borderTopLeftRadius:0,marginBottom:8}}>
              <div style={{fontSize:9,textTransform:"uppercase",color:C.tealDk,fontWeight:600,marginBottom:5,display:"flex",alignItems:"center",gap:5}}>
                <div style={{width:6,height:6,borderRadius:"50%",background:C.teal}}></div>Better You replied
              </div>
              {e.ai_reply?<div style={{fontSize:13,color:C.tealDk,lineHeight:1.7,fontStyle:"italic"}}>"{e.ai_reply}"</div>:<div><span className="td"/><span className="td"/><span className="td"/></div>}
            </div>
            {e.self_reply?(
              <div style={{background:C.roseLt,borderRadius:12,padding:"12px 14px",borderLeft:`3px solid ${C.rose}`,borderTopLeftRadius:0,marginBottom:8}}>
                <div style={{fontSize:9,textTransform:"uppercase",color:C.roseDk,fontWeight:600,marginBottom:5,display:"flex",alignItems:"center",gap:5}}>
                  <div style={{width:6,height:6,borderRadius:"50%",background:C.rose}}></div>You replied
                </div>
                <div style={{fontSize:13,color:C.roseDk,lineHeight:1.7}}>{e.self_reply}</div>
              </div>
            ):(
              <div className="card">
                <div style={{display:"flex",marginBottom:10,background:"#eee9e2",borderRadius:8,padding:2}}>
                  {[["self","Write self-response"],["ai","Ask AI"]].map(([t,l])=>(
                    <button key={t} onClick={()=>setCtab(t)} style={{flex:1,padding:"6px 0",fontSize:10,fontWeight:600,borderRadius:6,background:ctab===t?"white":"transparent",color:ctab===t?C.roseDk:C.mid,border:"none"}}>{l}</button>
                  ))}
                </div>
                {ctab==="self"?<>
                  <div style={{fontSize:10,color:C.mid,fontStyle:"italic",marginBottom:8}}>Write back to yourself — from where you are now.</div>
                  <textarea value={sr} onChange={e=>setSr(e.target.value)} placeholder="Looking back, I think..." className="ta" style={{minHeight:70,marginBottom:8}}/>
                  <button className="pbtn" onClick={saveSr} disabled={!sr.trim()}>Save my reply</button>
                </>:<>
                  <div style={{fontSize:10,color:C.mid,fontStyle:"italic",marginBottom:8}}>Ask Better You a follow-up question.</div>
                  <textarea value={afu} onChange={e=>setAfu(e.target.value)} placeholder="I'm curious about..." className="ta" style={{minHeight:70,marginBottom:8}}/>
                  <button className="pbtn" onClick={sendAfu} style={{background:C.tealDk}} disabled={loadAfu||!afu.trim()}>
                    {loadAfu?<><Spinner/>&nbsp;Thinking...</>:"Send to AI"}
                  </button>
                </>}
              </div>
            )}
            <div style={{display:"flex",gap:6,marginTop:4}}>
              {["📸","𝕏","👥","🔗"].map(d=><div key={d} style={{flex:1,border:".5px solid #e0dbd4",borderRadius:9,padding:"8px 3px",textAlign:"center",cursor:"pointer",background:"white",fontSize:16,color:C.mid}}>{d}</div>)}
            </div>
          </>
        )}
      </div>
      <Nav active="reflect" go={go}/>
    </div>
  );
}

// ── SHARE ──
function ShareScreen({go,user}) {
  const [entries,setEntries]=useState([]);
  const [selId,setSelId]=useState("");
  const [inc,setInc]=useState({entry:true,ai:true,self:true});
  const [anon,setAnon]=useState(false);
  const [dests,setDests]=useState({ig:true,tw:false,com:true,lnk:false});
  const [done,setDone]=useState(false);

  useEffect(()=>{
    supabase.from("entries").select("*").eq("user_id",user.id).order("entry_date",{ascending:false}).limit(5)
      .then(({data})=>{setEntries(data||[]);if(data?.length)setSelId(data[0].id);});
  },[user.id]);

  return (
    <div className="screen">
      <div className="hdr" style={{background:C.amberDk}}>
        <div className="back" onClick={()=>go("home")}>← home</div>
        <div className="htitle">Share your story</div>
        <div className="hsub">Choose exactly what the world sees</div>
      </div>
      <div className="body">
        {entries.length>0&&<><div className="slbl">Which entry</div>
          <select value={selId} onChange={e=>setSelId(e.target.value)} style={{width:"100%",padding:"11px 13px",borderRadius:10,border:".5px solid #e0dbd4",background:"white",fontSize:13,color:C.ink,marginBottom:14,fontFamily:"Nunito,sans-serif"}}>
            {entries.map(e=><option key={e.id} value={e.id}>{new Date(e.entry_date+"T00:00:00").toLocaleDateString("en-AU",{month:"short",day:"numeric"})} — {e.text.slice(0,40)}...</option>)}
          </select></>}
        <div className="slbl">Select what to include</div>
        <div className="card" style={{padding:0,overflow:"hidden",marginBottom:12}}>
          {[["entry","Your original entry",C.paper],["ai","AI reflection",C.tealLt],["self","Your self-response",C.roseLt]].map(([k,l,f])=>(
            <div key={k} onClick={()=>setInc(i=>({...i,[k]:!i[k]}))} style={{display:"flex",alignItems:"center",gap:12,padding:"12px 14px",borderBottom:".5px solid #f0ebe4",background:inc[k]?f:"white",cursor:"pointer"}}>
              <div style={{width:20,height:20,borderRadius:5,border:`1.5px solid ${inc[k]?C.amber:"#d0cac2"}`,background:inc[k]?C.amber:"white",display:"flex",alignItems:"center",justifyContent:"center",fontSize:12,color:"white",fontWeight:700,flexShrink:0}}>{inc[k]?"✓":""}</div>
              <div style={{fontSize:12,fontWeight:600,color:C.ink}}>{l}</div>
            </div>
          ))}
        </div>
        <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",background:C.amberLt,borderRadius:10,padding:"11px 13px",marginBottom:12}}>
          <div><div style={{fontSize:12,fontWeight:600,color:C.amberDk}}>Post anonymously</div><div style={{fontSize:10,color:C.amber,marginTop:2}}>Your name won't appear</div></div>
          <Toggle on={anon} color={C.amber} onChange={()=>setAnon(a=>!a)}/>
        </div>
        <div className="slbl">Share to</div>
        <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:8,marginBottom:16}}>
          {[["ig","📸 Instagram"],["tw","𝕏 Twitter"],["com","👥 Community"],["lnk","🔗 Copy link"]].map(([k,l])=>(
            <div key={k} onClick={()=>setDests(d=>({...d,[k]:!d[k]}))} style={{border:`1px solid ${dests[k]?C.amber:"#e0dbd4"}`,borderRadius:10,padding:"11px 8px",textAlign:"center",cursor:"pointer",background:dests[k]?C.amberLt:"white",fontSize:12,fontWeight:dests[k]?600:400,color:dests[k]?C.amberDk:C.mid}}>{l}</div>
          ))}
        </div>
        <button className="pbtn" style={{background:C.amberDk}} onClick={()=>{setDone(true);setTimeout(()=>setDone(false),2500);}}>
          {done?"✓ Published!":"Publish now"}
        </button>
      </div>
      <Nav active="home" go={go}/>
    </div>
  );
}

// ── CHEERS INBOX ──
function CheersScreen({go,user,cheers,setCheers}) {
  const markRead=async(id)=>{
    await supabase.from("cheers").update({is_read:true}).eq("id",id);
    setCheers(c=>c.map(x=>x.id===id?{...x,is_read:true}:x));
  };
  return (
    <div className="screen">
      <div className="hdr" style={{background:C.roseDk}}>
        <div className="back" onClick={()=>go("home")}>← home</div>
        <div className="htitle">Your cheers</div>
        <div className="hsub">People in your corner</div>
      </div>
      <div className="body">
        {cheers.length===0&&<div className="card" style={{textAlign:"center",padding:"32px 20px"}}>
          <div style={{fontSize:32,marginBottom:12}}>✦</div>
          <div style={{fontSize:14,fontWeight:600,color:C.ink,marginBottom:6}}>No cheers yet</div>
          <div style={{fontSize:12,color:C.mid}}>When friends send you encouragement it'll appear here.</div>
        </div>}
        {cheers.map(c=>(
          <div key={c.id} className="card" style={{borderColor:!c.is_read?"#F4C0D1":"#e8e2da"}} onClick={()=>markRead(c.id)}>
            <div style={{display:"flex",alignItems:"center",gap:10,marginBottom:8}}>
              <div style={{width:34,height:34,borderRadius:"50%",background:C.roseLt,display:"flex",alignItems:"center",justifyContent:"center",fontSize:13,fontWeight:700,color:C.roseDk,flexShrink:0}}>✦</div>
              <div style={{flex:1}}><div style={{fontSize:12,fontWeight:600,color:C.ink}}>A friend</div><div style={{fontSize:10,color:C.mid,marginTop:1}}>{c.type}</div></div>
              {!c.is_read&&<div style={{width:8,height:8,borderRadius:"50%",background:C.rose}}></div>}
            </div>
            {c.type==="prompt"&&<div style={{fontSize:12,color:C.ink,lineHeight:1.6,fontStyle:"italic"}}>"{c.content}"</div>}
            {c.type==="photo"&&<div style={{width:"100%",height:90,background:C.tealLt,borderRadius:8,display:"flex",alignItems:"center",justifyContent:"center",fontSize:36}}>🖼</div>}
            {c.type==="voice"&&<div style={{background:C.purpleLt,borderRadius:9,padding:"10px 12px",display:"flex",alignItems:"center",gap:10}}><div style={{width:30,height:30,borderRadius:"50%",background:C.purpleDk,display:"flex",alignItems:"center",justifyContent:"center",fontSize:13,color:"white"}}>▶</div><div style={{fontSize:11,color:C.purpleDk,fontWeight:600}}>Voice note</div></div>}
            <div style={{display:"flex",gap:6,marginTop:10}}>
              <button className="tag" style={{fontSize:11}}>♡ Love this</button>
              <button className="tag" style={{fontSize:11}}>↩ Reply</button>
            </div>
          </div>
        ))}
      </div>
      <Nav active="home" go={go}/>
    </div>
  );
}

// ── SEND CHEER ──
function SendCheerScreen({go,user}) {
  const [type,setType]=useState("prompt");
  const [msg,setMsg]=useState("");
  const [toUser,setToUser]=useState("");
  const [sending,setSending]=useState(false);
  const [err,setErr]=useState("");
  const [sent,setSent]=useState(false);

  const send=async()=>{
    if(!toUser.trim()||!msg.trim()){setErr("Please fill in all fields");return;}
    setSending(true);setErr("");
    const {data:profile}=await supabase.from("profiles").select("id").eq("username",toUser.trim()).single();
    if(!profile){setErr("Username not found. Ask them to check their username in settings.");setSending(false);return;}
    const {error}=await supabase.from("cheers").insert({from_user_id:user.id,to_user_id:profile.id,type,content:msg});
    if(error){setErr("Couldn't send. Try again.");setSending(false);return;}
    setSent(true);setTimeout(()=>go("home"),2000);
  };

  return (
    <div className="screen">
      <div className="hdr" style={{background:C.amberLt,paddingTop:52}}>
        <div className="back" style={{color:C.mid}} onClick={()=>go("home")}>← home</div>
        <div className="htitle" style={{color:C.roseDk}}>Send a cheer</div>
        <div className="hsub" style={{color:C.mid}}>Lift someone up today</div>
      </div>
      <div className="body">
        {err&&<div className="err">{err}</div>}
        {sent&&<div className="ok">✦ Cheer sent! They'll see it next time they open the app.</div>}
        <div className="card">
          <div className="slbl">Their username</div>
          <input className="inp" value={toUser} onChange={e=>setToUser(e.target.value)} placeholder="their_username" style={{marginBottom:0}}/>
        </div>
        <div style={{display:"flex",gap:0,background:"#eee9e2",borderRadius:10,padding:3,marginBottom:12}}>
          {[["prompt","✍ Prompt"],["photo","🖼 Photo"],["voice","🎙 Voice"]].map(([t,l])=>(
            <button key={t} onClick={()=>setType(t)} style={{flex:1,padding:"8px 0",fontSize:11,fontWeight:600,borderRadius:8,background:type===t?"white":"transparent",color:type===t?C.roseDk:C.mid,border:"none"}}>{l}</button>
          ))}
        </div>
        {type==="prompt"&&<div className="card">
          <div style={{fontSize:11,color:C.mid,fontStyle:"italic",marginBottom:8}}>Write an encouraging message or prompt.</div>
          <textarea value={msg} onChange={e=>setMsg(e.target.value)} placeholder="You've been showing up every day — that takes real courage..." className="ta" style={{minHeight:90}}/>
        </div>}
        {type==="photo"&&<div style={{background:C.paper,border:"1.5px dashed #d0cac2",borderRadius:12,padding:28,textAlign:"center"}}><div style={{fontSize:32,marginBottom:6}}>🖼</div><div style={{fontSize:13,color:C.mid}}>Photo sharing coming soon</div></div>}
        {type==="voice"&&<div style={{background:C.purpleLt,borderRadius:12,padding:24,textAlign:"center"}}><div style={{width:52,height:52,borderRadius:"50%",background:C.purpleDk,display:"flex",alignItems:"center",justifyContent:"center",margin:"0 auto 10px",fontSize:22,color:"white"}}>🎙</div><div style={{fontSize:13,color:C.purpleDk,fontWeight:600}}>Voice recording coming soon</div></div>}
        <button className="pbtn" style={{marginTop:14}} onClick={send} disabled={sending||sent}>
          {sending?<><Spinner/>&nbsp;Sending...</>:sent?"✦ Sent!":"Send cheer"}
        </button>
      </div>
      <Nav active="home" go={go}/>
    </div>
  );
}

// ── REMINDERS ──
function RemindersScreen({go,user}) {
  const [rem,setRem]=useState({journal_on:true,journal_time:"20:00",quote_on:true,quote_time:"07:30",weekly_on:true});
  const [saved,setSaved]=useState(false);
  const [username,setUsername]=useState("");
  const [savingUser,setSavingUser]=useState(false);

  useEffect(()=>{
    supabase.from("reminders").select("*").eq("user_id",user.id).single().then(({data})=>{if(data)setRem(data);});
    supabase.from("profiles").select("username").eq("id",user.id).single().then(({data})=>{if(data?.username)setUsername(data.username);});
  },[user.id]);

  const save=async()=>{
    await supabase.from("reminders").upsert({...rem,user_id:user.id});
    setSaved(true);setTimeout(()=>setSaved(false),2000);
  };

  const saveUsername=async()=>{
    if(!username.trim())return;
    setSavingUser(true);
    await supabase.from("profiles").update({username:username.trim()}).eq("id",user.id);
    setSavingUser(false);setSaved(true);setTimeout(()=>setSaved(false),2000);
  };

  const items=[
    {k:"journal",ic:"✍️",col:C.roseLt,txt:C.roseDk,ac:C.rose,n:"Daily journal nudge",s:"A gentle push to write each day",tk:"journal_time"},
    {k:"quote",  ic:"💬",col:C.amberLt,txt:C.amberDk,ac:C.amber,n:"Motivational quote",s:"An uplifting quote every morning",tk:"quote_time"},
    {k:"weekly", ic:"📊",col:C.tealLt, txt:C.tealDk, ac:C.teal, n:"Weekly reflection",s:"Sunday mood & entry summary",tk:null},
  ];

  return (
    <div className="screen">
      <div className="hdr" style={{background:C.purpleDk}}>
        <div className="back" onClick={()=>go("home")}>← home</div>
        <div className="htitle">Settings</div>
        <div className="hsub">Reminders & your profile</div>
      </div>
      <div className="body">
        {saved&&<div className="ok">Saved!</div>}
        <div className="card" style={{marginBottom:14}}>
          <div className="slbl">Your username</div>
          <div style={{fontSize:11,color:C.mid,marginBottom:8}}>Friends use this to send you cheers.</div>
          <div style={{display:"flex",gap:8}}>
            <input className="inp" value={username} onChange={e=>setUsername(e.target.value)} placeholder="choose_a_username" style={{flex:1,marginBottom:0}}/>
            <button className="pbtn" onClick={saveUsername} disabled={savingUser||!username.trim()} style={{width:"auto",padding:"12px 16px",background:C.purpleDk}}>{savingUser?<Spinner/>:"Save"}</button>
          </div>
        </div>
        <div className="slbl">Notifications</div>
        <div className="card" style={{padding:0,overflow:"hidden"}}>
          {items.map((item,i)=>(
            <div key={item.k} style={{padding:"13px 14px",borderBottom:i<items.length-1?".5px solid #f0ebe4":"none"}}>
              <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",marginBottom:4}}>
                <div style={{display:"flex",alignItems:"center",gap:10}}>
                  <div style={{width:30,height:30,borderRadius:8,background:item.col,display:"flex",alignItems:"center",justifyContent:"center",fontSize:14}}>{item.ic}</div>
                  <div style={{fontSize:13,fontWeight:600,color:C.ink}}>{item.n}</div>
                </div>
                <Toggle on={rem[`${item.k}_on`]} color={item.ac} onChange={()=>setRem(r=>({...r,[`${item.k}_on`]:!r[`${item.k}_on`]}))}/>
              </div>
              <div style={{fontSize:11,color:C.mid,marginBottom:item.tk?6:0}}>{item.s}</div>
              {item.tk&&<input type="time" value={rem[item.tk]} onChange={e=>setRem(r=>({...r,[item.tk]:e.target.value}))} style={{fontSize:11,fontWeight:600,color:item.txt,background:item.col,border:"none",borderRadius:7,padding:"4px 9px"}}/>}
            </div>
          ))}
        </div>
        <button className="pbtn" style={{marginTop:14,background:C.purpleDk}} onClick={save}>Save preferences</button>
        <div onClick={()=>supabase.auth.signOut()} style={{textAlign:"center",fontSize:11,color:C.mid,marginTop:16,cursor:"pointer",padding:"8px 0"}}>Sign out</div>
      </div>
      <Nav active="settings" go={go}/>
    </div>
  );
}

// ── ROOT ──
export default function App() {
  const [session,setSession]=useState(undefined);
  const [screen,setScreen]=useState("home");
  const [cheers,setCheers]=useState([]);
  const [rk,setRk]=useState(0);

  useEffect(()=>{
    supabase.auth.getSession().then(({data:{session}})=>setSession(session));
    const {data:{subscription}}=supabase.auth.onAuthStateChange((_,s)=>{
      setSession(s);
      if(s)loadCheers(s.user.id);
    });
    return()=>subscription.unsubscribe();
  },[]);

  const loadCheers=async(uid)=>{
    const {data}=await supabase.from("cheers").select("*").eq("to_user_id",uid).order("created_at",{ascending:false});
    setCheers(data||[]);
  };

  const go=useCallback(s=>setScreen(s),[]);
  const onSave=()=>setRk(k=>k+1);

  const Loading=()=><div style={{display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",minHeight:"100vh",background:C.roseDk}}><div style={{fontFamily:"'Playfair Display',serif",fontSize:44,color:"white",fontWeight:600,marginBottom:24}}>Better <em style={{color:"#F4C0D1"}}>You</em></div><Spinner color={C.roseLt}/></div>;

  if(session===undefined) return <><style>{css}</style><div className="phone"><Loading/></div></>;
  if(!session) return <><style>{css}</style><div className="phone"><AuthScreen/></div></>;

  const u=session.user;
  return (
    <>
      <style>{css}</style>
      <div className="phone">
        {screen==="home"      &&<HomeScreen go={go} user={u} cheers={cheers}/>}
        {screen==="entry"     &&<EntryScreen go={go} user={u} onSave={onSave}/>}
        {screen==="reflect"   &&<ReflectScreen go={go} user={u} rk={rk}/>}
        {screen==="share"     &&<ShareScreen go={go} user={u}/>}
        {screen==="cheers"    &&<CheersScreen go={go} user={u} cheers={cheers} setCheers={setCheers}/>}
        {screen==="sendCheer" &&<SendCheerScreen go={go} user={u}/>}
        {screen==="reminders" &&<RemindersScreen go={go} user={u}/>}
      </div>
    </>
  );
}
