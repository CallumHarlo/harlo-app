import { useState, useEffect, useCallback } from "react";
import { supabase } from "./supabase";

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
.phone{background:#FAF8F5;min-height:100vh;display:flex;flex-direction:column;}
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
.ni-l{font-size:9px;color:#6b6760;}
.ni.on .ni-l{color:#72243E;font-weight:600;}
.ni-d{width:4px;height:4px;border-radius:50%;background:#C9637A;display:none;margin:0 auto;}
.ni.on .ni-d{display:block;}
input,textarea{font-family:'Nunito',sans-serif;outline:none;}
button{font-family:'Nunito',sans-serif;cursor:pointer;border:none;}
.card{background:white;border-radius:14px;border:.5px solid #e8e2da;padding:14px;margin-bottom:10px;}
.tag{padding:6px 12px;border-radius:20px;font-size:11px;font-weight:600;border:.5px solid #e0dbd4;color:#6b6760;cursor:pointer;background:white;transition:all .15s;display:inline-flex;align-items:center;gap:5px;}
.tag.rz{background:#FBEAF0;border-color:#C9637A;color:#72243E;}
.tag.bz{background:#E6F1FB;border-color:#378ADD;color:#0C447C;}
.pbtn{background:#72243E;color:white;border-radius:12px;padding:13px;width:100%;font-size:14px;font-weight:600;transition:opacity .15s;}
.pbtn:disabled{opacity:.5;cursor:not-allowed;}
.slbl{font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:#6b6760;margin-bottom:8px;}
.spin{width:18px;height:18px;border:2px solid rgba(255,255,255,.3);border-top-color:white;border-radius:50%;animation:sp .7s linear infinite;display:inline-block;vertical-align:middle;}
@keyframes sp{to{transform:rotate(360deg)}}
.td{width:6px;height:6px;border-radius:50%;background:#1D9E75;animation:bo 1.2s infinite;display:inline-block;margin:0 2px;}
.td:nth-child(2){animation-delay:.2s}.td:nth-child(3){animation-delay:.4s}
@keyframes bo{0%,80%,100%{transform:scale(.6);opacity:.4}40%{transform:scale(1);opacity:1}}
.err{background:#FCEBEB;border:.5px solid #F09595;border-radius:10px;padding:10px 13px;font-size:12px;color:#A32D2D;margin-bottom:12px;}
.ok{background:#E1F5EE;border:.5px solid #1D9E75;border-radius:10px;padding:10px 13px;font-size:12px;color:#085041;margin-bottom:12px;}
.inp{width:100%;padding:12px 14px;border-radius:10px;border:.5px solid #e0dbd4;background:white;font-size:14px;color:#2C2A28;margin-bottom:14px;}
.ta{width:100%;background:#FAF8F5;border:.5px solid #e0dbd4;border-radius:10px;padding:11px 13px;font-size:13px;color:#2C2A28;resize:none;line-height:1.6;}
`;

async function getAI(text) {
  try {
    const r = await fetch("/api/ai-reflect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    const d = await r.json();
    return d.reply || "Thank you for sharing. Your feelings matter.";
  } catch (err) {
    return "Thank you for sharing that with me. Your feelings matter.";
  }
}

function Spinner({ color }) {
  return <div className="spin" style={color ? { borderTopColor: color } : {}}></div>;
}

function Nav({ active, go }) {
  return (
    <nav className="nav">
      {[["home","home","🏠"],["write","entry","✍️"],["reflect","reflect","💬"],["settings","reminders","⚙️"]].map(([k,sc,ic]) => (
        <div key={k} className={`ni${active===k?" on":""}`} onClick={() => go(sc)}>
          <span className="ni-i">{ic}</span>
          <div className="ni-d"></div>
          <span className="ni-l">{k}</span>
        </div>
      ))}
    </nav>
  );
}

function AuthScreen() {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [name, setName] = useState("");
  const [load, setLoad] = useState(false);
  const [err, setErr] = useState("");
  const [ok, setOk] = useState("");

  const submit = async () => {
    if (!email.trim() || !pw.trim()) { setErr("Please enter your email and password."); return; }
    setLoad(true); setErr(""); setOk("");
    try {
      if (mode === "login") {
        const { error } = await supabase.auth.signInWithPassword({ email: email.trim(), password: pw });
        if (error) setErr(error.message);
      } else {
        const displayName = name.trim() || email.split("@")[0];
        const { error } = await supabase.auth.signUp({ email: email.trim(), password: pw, options: { data: { display_name: displayName } } });
        if (error) setErr(error.message);
        else setOk("Account created! Check your email to confirm, then sign in.");
      }
    } catch (e) { setErr("Something went wrong. Please try again."); }
    setLoad(false);
  };

  return (
    <div className="screen" style={{ background: C.roseDk }}>
      <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "40px 0 20px" }}>
        <div style={{ fontFamily: "'Playfair Display',serif", fontSize: 44, color: "white", fontWeight: 600 }}>Better <em style={{ color: "#F4C0D1" }}>You</em></div>
        <div style={{ fontSize: 11, color: "rgba(255,255,255,.55)", letterSpacing: ".1em", textTransform: "uppercase", marginTop: 6 }}>Be good to yourself</div>
      </div>
      <div style={{ background: C.paper, borderRadius: "28px 28px 0 0", padding: "28px 24px 48px" }}>
        <div style={{ display: "flex", background: "#eee9e2", borderRadius: 10, padding: 3, marginBottom: 20 }}>
          {[["login","Sign in"],["signup","Sign up"]].map(([m,l]) => (
            <button key={m} onClick={() => { setMode(m); setErr(""); setOk(""); }} style={{ flex: 1, padding: "8px 0", fontSize: 13, fontWeight: 600, borderRadius: 8, background: mode===m?"white":"transparent", color: mode===m?C.roseDk:C.mid, border: "none" }}>{l}</button>
          ))}
        </div>
        {err && <div className="err">{err}</div>}
        {ok && <div className="ok">{ok}</div>}
        {mode === "signup" && <><div className="slbl">Your name (optional)</div><input className="inp" value={name} onChange={e => setName(e.target.value)} placeholder="What should we call you?" /></>}
        <div className="slbl">Email</div>
        <input className="inp" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="your@email.com" />
        <div className="slbl">Password</div>
        <input className="inp" type="password" value={pw} onChange={e => setPw(e.target.value)} placeholder="at least 6 characters" style={{ marginBottom: 20 }} />
        <button className="pbtn" onClick={submit} disabled={load}>
          {load ? <><Spinner />&nbsp;{mode==="login"?"Signing in...":"Creating account..."}</> : mode==="login"?"Sign in":"Create account"}
        </button>
      </div>
    </div>
  );
}

function HomeScreen({ go, user, cheers }) {
  const unread = cheers.filter(c => !c.is_read).length;
  const hr = new Date().getHours();
  const greet = hr < 12 ? "morning" : hr < 17 ? "afternoon" : "evening";
  const name = user?.user_metadata?.display_name || user?.email?.split("@")[0] || "there";
  return (
    <div className="screen">
      <div className="hdr" style={{ background: C.roseDk, paddingTop: 56 }}>
        <div style={{ fontSize: 11, color: "rgba(255,255,255,.55)" }}>Good {greet}</div>
        <div className="htitle">Hello, {name}</div>
        <div className="hsub">{new Date().toLocaleDateString("en-AU", { weekday: "long", month: "long", day: "numeric" })}</div>
      </div>
      <div className="body">
        {unread > 0 && (
          <div onClick={() => go("cheers")} style={{ background: C.roseLt, borderRadius: 14, padding: "12px 14px", border: ".5px solid #F4C0D1", marginBottom: 12, cursor: "pointer" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: C.roseDk }}>✦ Cheers for you</div>
              <div style={{ background: C.rose, color: "white", fontSize: 10, fontWeight: 700, padding: "2px 8px", borderRadius: 20 }}>{unread} new</div>
            </div>
            <div style={{ fontSize: 11, color: C.roseDk, fontStyle: "italic" }}>Tap to see messages from your supporters</div>
          </div>
        )}
        {[
          { ic:"✍️", t:"New entry", s:"Write how you feel today", col:C.roseLt, sc:"entry" },
          { ic:"💬", t:"Reply & reflect", s:"AI responds to your entries", col:C.tealLt, sc:"reflect" },
          { ic:"📤", t:"Publish entry", s:"Share to your community", col:C.amberLt, sc:"share" },
          { ic:"✦",  t:"Send a cheer", s:"Encourage someone you follow", col:C.roseLt, sc:"sendCheer" },
        ].map(card => (
          <div key={card.sc} onClick={() => go(card.sc)} className="card" style={{ display: "flex", alignItems: "center", gap: 12, cursor: "pointer" }}>
            <div style={{ width: 40, height: 40, borderRadius: 11, background: card.col, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, flexShrink: 0 }}>{card.ic}</div>
            <div style={{ flex: 1 }}><div style={{ fontSize: 14, fontWeight: 600, color: C.ink }}>{card.t}</div><div style={{ fontSize: 11, color: C.mid, marginTop: 1 }}>{card.s}</div></div>
            <div style={{ color: "#c0b8ae", fontSize: 18 }}>›</div>
          </div>
        ))}
        <div onClick={() => supabase.auth.signOut()} style={{ textAlign: "center", fontSize: 11, color: C.mid, marginTop: 20, cursor: "pointer", padding: "8px 0" }}>Sign out</div>
      </div>
      <Nav active="home" go={go} />
    </div>
  );
}

function EntryScreen({ go, user, onSave }) {
  const [text, setText] = useState("");
  const [tags, setTags] = useState([]);
  const [date, setDate] = useState(new Date().toISOString().split("T")[0]);
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState("");
  const allTags = [
    { l:"grateful", e:"🙂", s:"rz" }, { l:"anxious", e:"😰", s:"rz" },
    { l:"calm", e:"😌", s:"rz" }, { l:"sad", e:"😔", s:"bz" },
    { l:"hopeful", e:"🌱", s:"rz" }, { l:"proud", e:"✨", s:"rz" }
  ];
  const tog = l => setTags(t => t.includes(l) ? t.filter(x => x !== l) : [...t, l]);

  const save = async () => {
    if (!text.trim()) return;
    setSaving(true); setErr("");
    const ai = await getAI(text);
    const { error } = await supabase.from("entries").insert({ user_id: user.id, entry_date: date, text: text.trim(), tags, ai_reply: ai, self_reply: "" });
    if (error) { setErr("Could not save. Try again."); setSaving(false); return; }
    onSave(); go("reflect");
  };

  return (
    <div className="screen">
      <div className="hdr" style={{ background: C.roseDk }}>
        <div className="back" onClick={() => go("home")}>← back</div>
        <div className="htitle">New entry</div>
      </div>
      <div className="body">
        {err && <div className="err">{err}</div>}
        <div style={{ display: "flex", gap: 8, marginBottom: 14 }}>
          <div style={{ flex: 1, background: C.roseLt, borderRadius: 10, padding: "9px 12px" }}>
            <div style={{ fontSize: 9, textTransform: "uppercase", color: C.roseDk, marginBottom: 3 }}>Today</div>
            <div style={{ fontSize: 13, fontWeight: 600, color: C.roseDk }}>{new Date().toLocaleDateString("en-AU", { month: "short", day: "numeric", year: "numeric" })}</div>
          </div>
          <div style={{ flex: 1, background: C.tealLt, borderRadius: 10, padding: "9px 12px" }}>
            <div style={{ fontSize: 9, textTransform: "uppercase", color: C.tealDk, marginBottom: 3 }}>Select date</div>
            <input type="date" value={date} onChange={e => setDate(e.target.value)} style={{ fontSize: 11, fontWeight: 600, color: C.tealDk, background: "transparent", border: "none", width: "100%", padding: 0 }} />
          </div>
        </div>
        <textarea value={text} onChange={e => setText(e.target.value)} placeholder="Today I felt..." className="ta" style={{ minHeight: 140, borderRadius: 12, padding: "12px 14px", fontSize: 14, marginBottom: 14 }} />
        <div className="slbl">How are you feeling?</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 16 }}>
          {allTags.map(t => (
            <button key={t.l} className={`tag${tags.includes(t.l) ? " " + t.s : ""}`} onClick={() => tog(t.l)}>
              <span style={{ fontSize: 14 }}>{t.e}</span>{t.l}
            </button>
          ))}
        </div>
        <button className="pbtn" onClick={save} disabled={saving || !text.trim()}>
          {saving ? <><Spinner />&nbsp;Saving & getting reflection...</> : "Save entry"}
        </button>
      </div>
      <Nav active="write" go={go} />
    </div>
  );
}

function ReflectScreen({ go, user, rk }) {
  const [entries, setEntries] = useState([]);
  const [sel, setSel] = useState(0);
  const [sr, setSr] = useState("");
  const [ctab, setCtab] = useState("self");
  const [afu, setAfu] = useState("");
  const [loadAfu, setLoadAfu] = useState(false);
  const [loading, setLoading] = useState(true);
  const [currentAiReply, setCurrentAiReply] = useState("");

  const loadEntries = useCallback(async () => {
    setLoading(true);
    const { data } = await supabase.from("entries").select("*").eq("user_id", user.id).order("entry_date", { ascending: false }).limit(10);
    setEntries(data || []);
    if (data && data[sel]) setCurrentAiReply(data[sel].ai_reply || "");
    setLoading(false);
  }, [user.id, sel]);

  useEffect(() => { loadEntries(); }, [user.id, rk]);

  useEffect(() => {
    if (entries[sel]) setCurrentAiReply(entries[sel].ai_reply || "");
  }, [sel, entries]);

  const fmt = d => new Date(d + "T00:00:00").toLocaleDateString("en-AU", { month: "short", day: "numeric" });
  const e = entries[sel];

  const saveSr = async () => {
    await supabase.from("entries").update({ self_reply: sr }).eq("id", e.id);
    setEntries(prev => prev.map((x, i) => i === sel ? { ...x, self_reply: sr } : x));
    setSr("");
  };

  const sendAfu = async () => {
    if (!afu.trim()) return;
    setLoadAfu(true);
    const question = afu;
    setAfu("");
    const r = await getAI(`Original journal entry: "${e.text}". The user has a follow-up question: "${question}"`);
    await supabase.from("entries").update({ ai_reply: r }).eq("id", e.id);
    setCurrentAiReply(r);
    setEntries(prev => prev.map((x, i) => i === sel ? { ...x, ai_reply: r } : x));
    setLoadAfu(false);
  };

  if (loading) return <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "60vh" }}><Spinner color={C.teal} /></div>;

  return (
    <div className="screen">
      <div className="hdr" style={{ background: C.tealDk }}>
        <div className="back" onClick={() => go("home")}>← home</div>
        <div className="htitle">Reply & reflect</div>
        <div className="hsub">A conversation with yourself</div>
      </div>
      <div className="body">
        {entries.length === 0 ? (
          <div className="card" style={{ textAlign: "center", padding: "32px 20px" }}>
            <div style={{ fontSize: 32, marginBottom: 12 }}>✍️</div>
            <div style={{ fontSize: 14, fontWeight: 600, color: C.ink, marginBottom: 6 }}>No entries yet</div>
            <div style={{ fontSize: 12, color: C.mid, marginBottom: 16 }}>Write your first entry to get a reflection.</div>
            <button className="pbtn" onClick={() => go("entry")}>Write first entry</button>
          </div>
        ) : (
          <>
            <div style={{ display: "flex", gap: 6, marginBottom: 14, background: "#eee9e2", borderRadius: 10, padding: 3, overflowX: "auto" }}>
              {entries.slice(0, 4).map((en, i) => (
                <button key={en.id} onClick={() => setSel(i)} style={{ flex: "0 0 auto", padding: "7px 12px", fontSize: 11, fontWeight: 600, borderRadius: 8, background: sel===i?"white":"transparent", color: sel===i?C.tealDk:C.mid, border: "none", whiteSpace: "nowrap" }}>{fmt(en.entry_date)}</button>
              ))}
            </div>
            <div className="card" style={{ marginBottom: 8 }}>
              <div style={{ fontSize: 9, textTransform: "uppercase", color: C.mid, marginBottom: 6 }}>{fmt(e.entry_date)} · your entry</div>
              <div style={{ fontSize: 13, color: C.ink, lineHeight: 1.7 }}>"{e.text}"</div>
              {e.tags?.length > 0 && (
                <div style={{ display: "flex", gap: 5, flexWrap: "wrap", marginTop: 8 }}>
                  {e.tags.map(t => <span key={t} className={`tag ${t==="sad"?"bz":"rz"}`} style={{ fontSize: 10, padding: "3px 9px" }}>{t}</span>)}
                </div>
              )}
            </div>
            <div style={{ background: C.tealLt, borderRadius: 12, padding: "12px 14px", borderLeft: `3px solid ${C.teal}`, borderTopLeftRadius: 0, marginBottom: 8 }}>
              <div style={{ fontSize: 9, textTransform: "uppercase", color: C.tealDk, fontWeight: 600, marginBottom: 5, display: "flex", alignItems: "center", gap: 5 }}>
                <div style={{ width: 6, height: 6, borderRadius: "50%", background: C.teal }}></div>Better You replied
              </div>
              {currentAiReply
                ? <div style={{ fontSize: 13, color: C.tealDk, lineHeight: 1.7, fontStyle: "italic" }}>"{currentAiReply}"</div>
                : <div><span className="td" /><span className="td" /><span className="td" /></div>}
            </div>
            {e.self_reply && (
              <div style={{ background: C.roseLt, borderRadius: 12, padding: "12px 14px", borderLeft: `3px solid ${C.rose}`, borderTopLeftRadius: 0, marginBottom: 8 }}>
                <div style={{ fontSize: 9, textTransform: "uppercase", color: C.roseDk, fontWeight: 600, marginBottom: 5, display: "flex", alignItems: "center", gap: 5 }}>
                  <div style={{ width: 6, height: 6, borderRadius: "50%", background: C.rose }}></div>You replied
                </div>
                <div style={{ fontSize: 13, color: C.roseDk, lineHeight: 1.7 }}>{e.self_reply}</div>
              </div>
            )}
            <div className="card">
              <div style={{ display: "flex", marginBottom: 10, background: "#eee9e2", borderRadius: 8, padding: 2 }}>
                {[["self","Write self-response"],["ai","Ask AI follow-up"]].map(([t, l]) => (
                  <button key={t} onClick={() => setCtab(t)} style={{ flex: 1, padding: "6px 0", fontSize: 10, fontWeight: 600, borderRadius: 6, background: ctab===t?"white":"transparent", color: ctab===t?C.roseDk:C.mid, border: "none" }}>{l}</button>
                ))}
              </div>
              {ctab === "self" ? (
                <>
                  <div style={{ fontSize: 10, color: C.mid, fontStyle: "italic", marginBottom: 8 }}>Write back to yourself — from where you are now.</div>
                  <textarea value={sr} onChange={ev => setSr(ev.target.value)} placeholder="Looking back, I think..." className="ta" style={{ minHeight: 70, marginBottom: 8 }} />
                  <button className="pbtn" onClick={saveSr} disabled={!sr.trim()}>Save my reply</button>
                </>
              ) : (
                <>
                  <div style={{ fontSize: 10, color: C.mid, fontStyle: "italic", marginBottom: 8 }}>Ask Better You a follow-up question.</div>
                  <textarea value={afu} onChange={ev => setAfu(ev.target.value)} placeholder="I am curious about..." className="ta" style={{ minHeight: 70, marginBottom: 8 }} />
                  <button className="pbtn" onClick={sendAfu} style={{ background: C.tealDk }} disabled={loadAfu || !afu.trim()}>
                    {loadAfu ? <><Spinner />&nbsp;Thinking...</> : "Send to AI"}
                  </button>
                </>
              )}
            </div>
            <div style={{ display: "flex", gap: 6, marginTop: 4 }}>
              {["📸","𝕏","👥","🔗"].map(d => <div key={d} style={{ flex: 1, border: ".5px solid #e0dbd4", borderRadius: 9, padding: "8px 3px", textAlign: "center", cursor: "pointer", background: "white", fontSize: 16, color: C.mid }}>{d}</div>)}
            </div>
          </>
        )}
      </div>
      <Nav active="reflect" go={go} />
    </div>
  );
}

function ShareScreen({ go, user }) {
  const [entries, setEntries] = useState([]);
  const [selId, setSelId] = useState("");
  const [inc, setInc] = useState({ entry: true, ai: true, self: true });
  const [anon, setAnon] = useState(false);
  const [dests, setDests] = useState({ ig: true, tw: false, com: true, lnk: false });
  const [done, setDone] = useState(false);

  useEffect(() => {
    supabase.from("entries").select("*").eq("user_id", user.id).order("entry_date", { ascending: false }).limit(5)
      .then(({ data }) => { setEntries(data || []); if (data?.length) setSelId(data[0].id); });
  }, [user.id]);

  return (
    <div className="screen">
      <div className="hdr" style={{ background: C.amberDk }}>
        <div className="back" onClick={() => go("home")}>← home</div>
        <div className="htitle">Share your story</div>
        <div className="hsub">Choose exactly what the world sees</div>
      </div>
      <div className="body">
        {entries.length > 0 && (
          <><div className="slbl">Which entry</div>
          <select value={selId} onChange={e => setSelId(e.target.value)} style={{ width: "100%", padding: "11px 13px", borderRadius: 10, border: ".5px solid #e0dbd4", background: "white", fontSize: 13, color: C.ink, marginBottom: 14, fontFamily: "Nunito,sans-serif" }}>
            {entries.map(e => <option key={e.id} value={e.id}>{new Date(e.entry_date + "T00:00:00").toLocaleDateString("en-AU", { month: "short", day: "numeric" })} — {e.text.slice(0, 40)}...</option>)}
          </select></>
        )}
        <div className="slbl">Select what to include</div>
        <div className="card" style={{ padding: 0, overflow: "hidden", marginBottom: 12 }}>
          {[["entry","Your original entry",C.paper],["ai","AI reflection",C.tealLt],["self","Your self-response",C.roseLt]].map(([k,l,f]) => (
            <div key={k} onClick={() => setInc(i => ({ ...i, [k]: !i[k] }))} style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 14px", borderBottom: ".5px solid #f0ebe4", background: inc[k]?f:"white", cursor: "pointer" }}>
              <div style={{ width: 20, height: 20, borderRadius: 5, border: `1.5px solid ${inc[k]?C.amber:"#d0cac2"}`, background: inc[k]?C.amber:"white", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, color: "white", fontWeight: 700, flexShrink: 0 }}>{inc[k]?"✓":""}</div>
              <div style={{ fontSize: 12, fontWeight: 600, color: C.ink }}>{l}</div>
            </div>
          ))}
        </div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", background: C.amberLt, borderRadius: 10, padding: "11px 13px", marginBottom: 12 }}>
          <div><div style={{ fontSize: 12, fontWeight: 600, color: C.amberDk }}>Post anonymously</div><div style={{ fontSize: 10, color: C.amber, marginTop: 2 }}>Your name won't appear</div></div>
          <div onClick={() => setAnon(a => !a)} style={{ width: 38, height: 22, borderRadius: 11, background: anon?C.amber:"#d0cac2", position: "relative", cursor: "pointer", transition: "background .2s" }}>
            <div style={{ width: 18, height: 18, borderRadius: "50%", background: "white", position: "absolute", top: 2, left: anon?18:2, transition: "left .2s" }}></div>
          </div>
        </div>
        <div className="slbl">Share to</div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 16 }}>
          {[["ig","📸 Instagram"],["tw","𝕏 Twitter"],["com","👥 Community"],["lnk","🔗 Copy link"]].map(([k,l]) => (
            <div key={k} onClick={() => setDests(d => ({ ...d, [k]: !d[k] }))} style={{ border: `1px solid ${dests[k]?C.amber:"#e0dbd4"}`, borderRadius: 10, padding: "11px 8px", textAlign: "center", cursor: "pointer", background: dests[k]?C.amberLt:"white", fontSize: 12, fontWeight: dests[k]?600:400, color: dests[k]?C.amberDk:C.mid }}>{l}</div>
          ))}
        </div>
        <button className="pbtn" style={{ background: C.amberDk }} onClick={() => { setDone(true); setTimeout(() => setDone(false), 2500); }}>
          {done ? "✓ Published!" : "Publish now"}
        </button>
      </div>
      <Nav active="home" go={go} />
    </div>
  );
}

function CheersScreen({ go, cheers, setCheers }) {
  const markRead = async id => {
    await supabase.from("cheers").update({ is_read: true }).eq("id", id);
    setCheers(c => c.map(x => x.id === id ? { ...x, is_read: true } : x));
  };
  return (
    <div className="screen">
      <div className="hdr" style={{ background: C.roseDk }}>
        <div className="back" onClick={() => go("home")}>← home</div>
        <div className="htitle">Your cheers</div>
        <div className="hsub">People in your corner</div>
      </div>
      <div className="body">
        {cheers.length === 0 && (
          <div className="card" style={{ textAlign: "center", padding: "32px 20px" }}>
            <div style={{ fontSize: 32, marginBottom: 12 }}>✦</div>
            <div style={{ fontSize: 14, fontWeight: 600, color: C.ink, marginBottom: 6 }}>No cheers yet</div>
            <div style={{ fontSize: 12, color: C.mid }}>When friends send you encouragement it'll appear here.</div>
          </div>
        )}
        {cheers.map(c => (
          <div key={c.id} className="card" style={{ borderColor: !c.is_read?"#F4C0D1":"#e8e2da" }} onClick={() => markRead(c.id)}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
              <div style={{ width: 34, height: 34, borderRadius: "50%", background: C.roseLt, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, fontWeight: 700, color: C.roseDk, flexShrink: 0 }}>✦</div>
              <div style={{ flex: 1 }}><div style={{ fontSize: 12, fontWeight: 600, color: C.ink }}>A friend</div><div style={{ fontSize: 10, color: C.mid, marginTop: 1 }}>{c.type}</div></div>
              {!c.is_read && <div style={{ width: 8, height: 8, borderRadius: "50%", background: C.rose }}></div>}
            </div>
            {c.type === "prompt" && <div style={{ fontSize: 12, color: C.ink, lineHeight: 1.6, fontStyle: "italic" }}>"{c.content}"</div>}
            {c.type === "photo" && <div style={{ width: "100%", height: 90, background: C.tealLt, borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 36 }}>🖼</div>}
            {c.type === "voice" && (
              <div style={{ background: C.purpleLt, borderRadius: 9, padding: "10px 12px", display: "flex", alignItems: "center", gap: 10 }}>
                <div style={{ width: 30, height: 30, borderRadius: "50%", background: C.purpleDk, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, color: "white" }}>▶</div>
                <div style={{ fontSize: 11, color: C.purpleDk, fontWeight: 600 }}>Voice note</div>
              </div>
            )}
            <div style={{ display: "flex", gap: 6, marginTop: 10 }}>
              <button className="tag" style={{ fontSize: 11 }}>♡ Love this</button>
              <button className="tag" style={{ fontSize: 11 }}>↩ Reply</button>
            </div>
          </div>
        ))}
      </div>
      <Nav active="home" go={go} />
    </div>
  );
}

function SendCheerScreen({ go, user }) {
  const [type, setType] = useState("prompt");
  const [msg, setMsg] = useState("");
  const [toUser, setToUser] = useState("");
  const [sending, setSending] = useState(false);
  const [err, setErr] = useState("");
  const [sent, setSent] = useState(false);

  const send = async () => {
    if (!toUser.trim() || !msg.trim()) { setErr("Please fill in all fields"); return; }
    setSending(true); setErr("");
    const { data: profile } = await supabase.from("profiles").select("id").eq("username", toUser.trim()).single();
    if (!profile) { setErr("Username not found."); setSending(false); return; }
    const { error } = await supabase.from("cheers").insert({ from_user_id: user.id, to_user_id: profile.id, type, content: msg });
    if (error) { setErr("Could not send. Try again."); setSending(false); return; }
    setSent(true); setTimeout(() => go("home"), 2000);
  };

  return (
    <div className="screen">
      <div className="hdr" style={{ background: C.amberLt, paddingTop: 52 }}>
        <div className="back" style={{ color: C.mid }} onClick={() => go("home")}>← home</div>
        <div className="htitle" style={{ color: C.roseDk }}>Send a cheer</div>
        <div className="hsub" style={{ color: C.mid }}>Lift someone up today</div>
      </div>
      <div className="body">
        {err && <div className="err">{err}</div>}
        {sent && <div className="ok">✦ Cheer sent!</div>}
        <div className="card">
          <div className="slbl">Their username</div>
          <input className="inp" value={toUser} onChange={e => setToUser(e.target.value)} placeholder="their_username" style={{ marginBottom: 0 }} />
        </div>
        <div style={{ display: "flex", gap: 0, background: "#eee9e2", borderRadius: 10, padding: 3, marginBottom: 12 }}>
          {[["prompt","✍ Prompt"],["photo","🖼 Photo"],["voice","🎙 Voice"]].map(([t, l]) => (
            <button key={t} onClick={() => setType(t)} style={{ flex: 1, padding: "8px 0", fontSize: 11, fontWeight: 600, borderRadius: 8, background: type===t?"white":"transparent", color: type===t?C.roseDk:C.mid, border: "none" }}>{l}</button>
          ))}
        </div>
        {type === "prompt" && (
          <div className="card">
            <textarea value={msg} onChange={e => setMsg(e.target.value)} placeholder="You've been showing up every day — that takes real courage..." className="ta" style={{ minHeight: 90 }} />
          </div>
        )}
        {type !== "prompt" && <div style={{ background: C.purpleLt, borderRadius: 12, padding: 24, textAlign: "center" }}><div style={{ fontSize: 13, color: C.purpleDk, fontWeight: 600 }}>Coming soon</div></div>}
        <button className="pbtn" style={{ marginTop: 14 }} onClick={send} disabled={sending || sent}>
          {sending ? <><Spinner />&nbsp;Sending...</> : sent ? "✦ Sent!" : "Send cheer"}
        </button>
      </div>
      <Nav active="home" go={go} />
    </div>
  );
}

function RemindersScreen({ go, user }) {
  const [rem, setRem] = useState({ journal_on: true, journal_time: "20:00", quote_on: true, quote_time: "07:30", weekly_on: true });
  const [saved, setSaved] = useState(false);
  const [username, setUsername] = useState("");

  useEffect(() => {
    supabase.from("reminders").select("*").eq("user_id", user.id).single().then(({ data }) => { if (data) setRem(data); });
    supabase.from("profiles").select("username").eq("id", user.id).single().then(({ data }) => { if (data?.username) setUsername(data.username); });
  }, [user.id]);

  const save = async () => {
    await supabase.from("reminders").upsert({ ...rem, user_id: user.id });
    if (username.trim()) await supabase.from("profiles").update({ username: username.trim() }).eq("id", user.id);
    setSaved(true); setTimeout(() => setSaved(false), 2000);
  };

  const items = [
    { k:"journal", ic:"✍️", col:C.roseLt, txt:C.roseDk, ac:C.rose, n:"Daily journal nudge", s:"A gentle push to write each day", tk:"journal_time" },
    { k:"quote",   ic:"💬", col:C.amberLt, txt:C.amberDk, ac:C.amber, n:"Motivational quote", s:"An uplifting quote every morning", tk:"quote_time" },
    { k:"weekly",  ic:"📊", col:C.tealLt,  txt:C.tealDk,  ac:C.teal,  n:"Weekly reflection", s:"Sunday mood & entry summary", tk:null },
  ];

  return (
    <div className="screen">
      <div className="hdr" style={{ background: C.purpleDk }}>
        <div className="back" onClick={() => go("home")}>← home</div>
        <div className="htitle">Settings</div>
        <div className="hsub">Profile & reminders</div>
      </div>
      <div className="body">
        {saved && <div className="ok">Saved!</div>}
        <div className="card" style={{ marginBottom: 14 }}>
          <div className="slbl">Your username</div>
          <div style={{ fontSize: 11, color: C.mid, marginBottom: 8 }}>Friends use this to send you cheers.</div>
          <input className="inp" value={username} onChange={e => setUsername(e.target.value)} placeholder="choose_a_username" style={{ marginBottom: 0 }} />
        </div>
        <div className="slbl">Notifications</div>
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          {items.map((item, i) => (
            <div key={item.k} style={{ padding: "13px 14px", borderBottom: i < items.length-1?".5px solid #f0ebe4":"none" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 4 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <div style={{ width: 30, height: 30, borderRadius: 8, background: item.col, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14 }}>{item.ic}</div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: C.ink }}>{item.n}</div>
                </div>
                <div onClick={() => setRem(r => ({ ...r, [`${item.k}_on`]: !r[`${item.k}_on`] }))} style={{ width: 38, height: 22, borderRadius: 11, background: rem[`${item.k}_on`]?item.ac:"#d0cac2", position: "relative", cursor: "pointer", transition: "background .2s" }}>
                  <div style={{ width: 18, height: 18, borderRadius: "50%", background: "white", position: "absolute", top: 2, left: rem[`${item.k}_on`]?18:2, transition: "left .2s" }}></div>
                </div>
              </div>
              <div style={{ fontSize: 11, color: C.mid, marginBottom: item.tk?6:0 }}>{item.s}</div>
              {item.tk && <input type="time" value={rem[item.tk]} onChange={e => setRem(r => ({ ...r, [item.tk]: e.target.value }))} style={{ fontSize: 11, fontWeight: 600, color: item.txt, background: item.col, border: "none", borderRadius: 7, padding: "4px 9px" }} />}
            </div>
          ))}
        </div>
        <button className="pbtn" style={{ marginTop: 14, background: C.purpleDk }} onClick={save}>Save preferences</button>
        <div onClick={() => supabase.auth.signOut()} style={{ textAlign: "center", fontSize: 11, color: C.mid, marginTop: 16, cursor: "pointer", padding: "8px 0" }}>Sign out</div>
      </div>
      <Nav active="settings" go={go} />
    </div>
  );
}

export default function App() {
  const [session, setSession] = useState(undefined);
  const [screen, setScreen] = useState("home");
  const [cheers, setCheers] = useState([]);
  const [rk, setRk] = useState(0);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => setSession(session));
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_, s) => {
      setSession(s);
      if (s) loadCheers(s.user.id);
    });
    return () => subscription.unsubscribe();
  }, []);

  const loadCheers = async uid => {
    const { data } = await supabase.from("cheers").select("*").eq("to_user_id", uid).order("created_at", { ascending: false });
    setCheers(data || []);
  };

  const go = useCallback(s => setScreen(s), []);
  const onSave = () => setRk(k => k + 1);

  if (session === undefined) return (
    <>
      <style>{css}</style>
      <div className="phone" style={{ alignItems: "center", justifyContent: "center", background: C.roseDk }}>
        <div style={{ fontFamily: "'Playfair Display',serif", fontSize: 44, color: "white", fontWeight: 600, marginBottom: 24 }}>Better <em style={{ color: "#F4C0D1" }}>You</em></div>
        <Spinner color="#F4C0D1" />
      </div>
    </>
  );

  if (!session) return <><style>{css}</style><div className="phone"><AuthScreen /></div></>;

  const u = session.user;
  return (
    <>
      <style>{css}</style>
      <div className="phone">
        {screen === "home"      && <HomeScreen go={go} user={u} cheers={cheers} />}
        {screen === "entry"     && <EntryScreen go={go} user={u} onSave={onSave} />}
        {screen === "reflect"   && <ReflectScreen go={go} user={u} rk={rk} />}
        {screen === "share"     && <ShareScreen go={go} user={u} />}
        {screen === "cheers"    && <CheersScreen go={go} cheers={cheers} setCheers={setCheers} />}
        {screen === "sendCheer" && <SendCheerScreen go={go} user={u} />}
        {screen === "reminders" && <RemindersScreen go={go} user={u} />}
      </div>
    </>
  );
}
