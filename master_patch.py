import { useState, useEffect, useCallback } from "react";
import { supabase } from "./supabase";

function getWeekDates() {
  const d = new Date();
  const diff = (d.getDay() + 6) % 7;
  return Array.from({ length: 7 }, (_, i) => {
    const date = new Date(d);
    date.setDate(d.getDate() - diff + i);
    return date.toISOString().split("T")[0];
  });
}

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
      {[["home","home","🏠"],["write","entry","✍️"],["reflect","reflect","💬"],["community","community","👥"],["settings","profile","⚙️"]].map(([k,sc,ic]) => (
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
        {mode === "login" && (
          <div style={{ textAlign: "center", marginTop: 14 }}>
            <button onClick={async () => {
              if (!email.trim()) { setErr("Enter your email above first."); return; }
              setLoad(true); setErr(""); setOk("");
              const { error } = await supabase.auth.resetPasswordForEmail(email.trim(), { redirectTo: window.location.origin });
              setLoad(false);
              if (error) setErr(error.message);
              else setOk("Password reset email sent! Check your inbox.");
            }} style={{ background: "none", border: "none", fontSize: 12, color: C.mid, cursor: "pointer", textDecoration: "underline" }}>
              Forgot password?
            </button>
          </div>
        )}
        {mode === "signup" && (
          <div style={{ textAlign: "center", marginTop: 12, fontSize: 11, color: C.mid, lineHeight: 1.6 }}>
            By signing up you agree to our Terms of Service and Privacy Policy
          </div>
        )}
      </div>
    </div>
  );
}

function HomeScreen({ go, user, cheers }) {
  const unread = cheers.filter(c => !c.is_read).length;
  const hr = new Date().getHours();
  const greet = hr < 12 ? "morning" : hr < 17 ? "afternoon" : "evening";
  const name = user?.user_metadata?.display_name || user?.email?.split("@")[0] || "there";
  const today = new Date().toISOString().split("T")[0];
  const [quote, setQuote] = useState("");
  const [streak, setStreak] = useState(0);
  const [weekMoods, setWeekMoods] = useState([null,null,null,null,null,null,null]);
  const [todayMood, setTodayMood] = useState(null);
  const [savingMood, setSavingMood] = useState(false);
  const [promptIdx, setPromptIdx] = useState(0);
  const PROMPTS = [
    "What moment from today deserves to be remembered?",
    "What emotion have you been carrying without naming?",
    "What would you tell yourself one week ago?",
    "Where did you surprise yourself recently?",
    "What does 'enough' look like for you today?",
    "What's one thing you want to let go of this week?",
    "What made you smile genuinely today?",
  ];
  const MOODS = [
    { l:"Great", e:"😄", score:5 },
    { l:"Good",  e:"🙂", score:4 },
    { l:"Okay",  e:"😐", score:3 },
    { l:"Low",   e:"😔", score:2 },
    { l:"Hard",  e:"😞", score:1 },
  ];
  useEffect(() => {
    const weekDates = getWeekDates();
    setPromptIdx(Math.floor(Math.random() * PROMPTS.length));
    supabase.from("profiles").select("daily_quote,quote_date").eq("id", user.id).single()
      .then(async ({ data }) => {
        if (data?.daily_quote && data?.quote_date === today) { setQuote(data.daily_quote); return; }
        const { data: entries } = await supabase.from("entries").select("tags").eq("user_id", user.id).order("created_at", { ascending: false }).limit(5);
        const moods = entries?.flatMap(e => e.tags || []).join(", ") || "general wellbeing";
        const r = await fetch("/api/ai-reflect", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: "Write a short motivational quote (1 sentence, max 15 words) for someone with moods: " + moods + ". Be warm." }) });
        const d2 = await r.json();
        const q = d2.reply || "You are doing better than you think.";
        setQuote(q);
        supabase.from("profiles").update({ daily_quote: q, quote_date: today }).eq("id", user.id);
      });
    supabase.from("mood_logs").select("log_date,mood_score,mood_label")
      .eq("user_id", user.id).gte("log_date", weekDates[0]).lte("log_date", weekDates[6])
      .then(({ data }) => {
        const map = {};
        (data || []).forEach(m => { map[m.log_date] = m; });
        setWeekMoods(weekDates.map(d => map[d] || null));
        if (map[today]) setTodayMood(map[today].mood_score);
      });
    supabase.from("mood_logs").select("log_date").eq("user_id", user.id)
      .order("log_date", { ascending: false }).limit(60)
      .then(({ data }) => {
        if (!data || data.length === 0) { setStreak(0); return; }
        const dates = data.map(d => d.log_date);
        let count = 0;
        const check = new Date();
        if (!dates.includes(check.toISOString().split("T")[0])) check.setDate(check.getDate() - 1);
        while (true) {
          const s = check.toISOString().split("T")[0];
          if (dates.includes(s)) { count++; check.setDate(check.getDate() - 1); } else break;
        }
        setStreak(count);
      });
  }, [user.id]);
  const logMood = async (mood) => {
    if (savingMood) return;
    if (navigator.vibrate) navigator.vibrate(10);
    setSavingMood(true);
    setTodayMood(mood.score);
    const weekDates = getWeekDates();
    const todayIdx = weekDates.indexOf(today);
    setWeekMoods(prev => prev.map((m, i) => i === todayIdx ? { mood_score: mood.score, mood_label: mood.l, log_date: today } : m));
    await supabase.from("mood_logs").upsert(
      { user_id: user.id, log_date: today, mood_score: mood.score, mood_label: mood.l },
      { onConflict: "user_id,log_date" }
    );
    setSavingMood(false);
  };
  const DAY_LABELS = ["M","T","W","T","F","S","S"];
  const weekDates = getWeekDates();
  const todayIdx = weekDates.indexOf(today);
  return (
    <div className="screen">
      <div style={{ background: C.roseDk, paddingTop: 52, paddingBottom: 20, paddingLeft: 20, paddingRight: 20 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
          <div>
            <div style={{ fontSize: 11, color: "rgba(255,255,255,.55)" }}>Good {greet}</div>
            <div style={{ fontFamily: "'Playfair Display',serif", fontSize: 24, color: "white", fontWeight: 600 }}>Hello, {name}</div>
            <div style={{ fontSize: 11, color: "rgba(255,255,255,.45)", marginTop: 2 }}>{new Date().toLocaleDateString("en-AU", { weekday: "long", month: "long", day: "numeric" })}</div>
          </div>
          {streak > 0 && (
            <div style={{ display: "flex", alignItems: "center", gap: 6, background: "rgba(255,255,255,.15)", borderRadius: 99, padding: "6px 12px" }}>
              <span style={{ fontSize: 16 }}>🔥</span>
              <div>
                <div style={{ fontSize: 16, fontWeight: 700, color: "white", lineHeight: 1 }}>{streak}</div>
                <div style={{ fontSize: 9, color: "rgba(255,255,255,.7)", lineHeight: 1, marginTop: 2 }}>day streak</div>
              </div>
            </div>
          )}
        </div>
        <div style={{ background: "rgba(0,0,0,0.2)", borderRadius: 14, padding: "12px 14px" }}>
          <div style={{ fontSize: 9, textTransform: "uppercase", letterSpacing: ".08em", color: "rgba(255,255,255,.55)", fontWeight: 600, marginBottom: 10 }}>How are you feeling today?</div>
          <div style={{ display: "flex", gap: 6 }}>
            {MOODS.map(m => (
              <button key={m.score} onClick={() => logMood(m)} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 3, padding: "8px 4px", borderRadius: 10, border: "none", background: todayMood === m.score ? "rgba(255,255,255,.3)" : "rgba(255,255,255,.1)", cursor: "pointer" }}>
                <span style={{ fontSize: 20 }}>{m.e}</span>
                <span style={{ fontSize: 9, color: "rgba(255,255,255,.7)", fontWeight: 600 }}>{m.l}</span>
              </button>
            ))}
          </div>
          <div style={{ display: "flex", gap: 5, justifyContent: "center", marginTop: 10 }}>
            {weekMoods.map((m, i) => (
              <div key={i} style={{ width: i === todayIdx ? 10 : 8, height: i === todayIdx ? 10 : 8, borderRadius: "50%", background: m ? "#F4C0D1" : "rgba(255,255,255,.2)", outline: i === todayIdx ? "2px solid rgba(255,255,255,.5)" : "none" }} />
            ))}
          </div>
        </div>
      </div>
      <div className="body">
        <div className="card" style={{ marginBottom: 12 }}>
          <div className="slbl" style={{ marginBottom: 10 }}>Mood this week</div>
          <div style={{ display: "flex", alignItems: "flex-end", gap: 6, height: 70 }}>
            {weekMoods.map((m, i) => (
              <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                <div style={{ width: "100%", height: m ? `${(m.mood_score / 5) * 56}px` : "6px", borderRadius: 6, background: i === todayIdx ? C.rose : m ? C.roseDk : "#e8e2da", opacity: m ? 1 : 0.4 }} />
                <div style={{ fontSize: 9, color: i === todayIdx ? C.roseDk : C.mid, fontWeight: i === todayIdx ? 700 : 400 }}>{DAY_LABELS[i]}</div>
              </div>
            ))}
          </div>
        </div>
        <div onClick={() => go("entry")} style={{ background: C.amberLt, borderRadius: 14, padding: "12px 14px", border: `.5px solid ${C.amber}`, marginBottom: 12, cursor: "pointer" }}>
          <div style={{ fontSize: 9, textTransform: "uppercase", letterSpacing: ".08em", color: C.amberDk, fontWeight: 600, marginBottom: 6 }}>✦ Today's prompt</div>
          <div style={{ fontSize: 13, color: C.amberDk, lineHeight: 1.6, fontStyle: "italic" }}>{PROMPTS[promptIdx]}</div>
          <div style={{ fontSize: 11, color: C.amber, marginTop: 6 }}>Tap to write →</div>
        </div>
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
          { ic:"✦",  t:"Send a cheer", s:"Encourage a friend", col:C.roseLt, sc:"cheers" },
          { ic:"👥", t:"Community", s:"Connect with others", col:C.purpleLt, sc:"community" },
          { ic:"🆘", t:"I'm struggling", s:"Breathing, grounding & helplines", col:"#e8e8f0", sc:"crisis" },
        ].map(card => (
          <div key={card.sc} onClick={() => go(card.sc)} className="card" style={{ display: "flex", alignItems: "center", gap: 12, cursor: "pointer" }}>
            <div style={{ width: 40, height: 40, borderRadius: 11, background: card.col, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, flexShrink: 0 }}>{card.ic}</div>
            <div style={{ flex: 1 }}><div style={{ fontSize: 14, fontWeight: 600, color: C.ink }}>{card.t}</div><div style={{ fontSize: 11, color: C.mid, marginTop: 1 }}>{card.s}</div></div>
            <div style={{ color: "#c0b8ae", fontSize: 18 }}>›</div>
          </div>
        ))}
        {quote && (
          <div style={{ background: "#EEEDFE", borderRadius: 14, padding: "14px 16px", border: ".5px solid #7F77DD", marginTop: 4 }}>
            <div style={{ fontSize: 9, textTransform: "uppercase", letterSpacing: ".1em", color: "#3C3489", marginBottom: 6, fontWeight: 600 }}>✦ Your daily quote</div>
            <div style={{ fontSize: 13, color: "#3C3489", lineHeight: 1.7, fontStyle: "italic" }}>{quote.replace(/\*\*/g,'').replace(/\*/g,'')}</div>
          </div>
        )}
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
  const [view, setView] = useState("timeline");
  const [moodFilter, setMoodFilter] = useState(null);

  const loadEntries = useCallback(async () => {
    setLoading(true);
    const { data } = await supabase.from("entries").select("*").eq("user_id", user.id).order("entry_date", { ascending: false }).limit(10);
    setEntries(data || []);
    setSel(0);
    if (data && data[0]) setCurrentAiReply(data[0].ai_reply || "");
    setLoading(false);
  }, [user.id, rk]);

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
            <div style={{ display: "flex", gap: 0, background: "#eee9e2", borderRadius: 10, padding: 3, marginBottom: 14 }}>
              {[["timeline","Timeline"],["moods","By mood"]].map(([v,l]) => (
                <button key={v} onClick={() => { setView(v); setMoodFilter(null); }} style={{ flex: 1, padding: "7px 0", fontSize: 11, fontWeight: 600, borderRadius: 8, background: view===v?"white":"transparent", color: view===v?C.tealDk:C.mid, border: "none" }}>{l}</button>
              ))}
            </div>

            {view === "moods" && (
              <>
                {!moodFilter ? (
                  <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 14 }}>
                    {[
                      { tag: "grateful", emoji: "🙂", color: C.roseLt, txt: C.roseDk, border: C.rose },
                      { tag: "anxious",  emoji: "😰", color: C.amberLt, txt: C.amberDk, border: C.amber },
                      { tag: "calm",     emoji: "😌", color: C.tealLt, txt: C.tealDk, border: C.teal },
                      { tag: "sad",      emoji: "😔", color: C.blueLt, txt: C.blueDk, border: C.blue },
                      { tag: "hopeful",  emoji: "🌱", color: C.tealLt, txt: C.tealDk, border: C.teal },
                      { tag: "proud",    emoji: "✨", color: C.purpleLt, txt: C.purpleDk, border: C.purple },
                    ].map(m => {
                      const count = entries.filter(e => e.tags?.includes(m.tag)).length;
                      return (
                        <div key={m.tag} onClick={() => { if(count > 0) setMoodFilter(m.tag); }} style={{ display: "flex", alignItems: "center", gap: 12, background: m.color, borderRadius: 12, padding: "12px 14px", border: `.5px solid ${m.border}`, cursor: count > 0 ? "pointer" : "default", opacity: count > 0 ? 1 : 0.4 }}>
                          <span style={{ fontSize: 22 }}>{m.emoji}</span>
                          <div style={{ flex: 1 }}>
                            <div style={{ fontSize: 13, fontWeight: 600, color: m.txt, textTransform: "capitalize" }}>{m.tag}</div>
                            <div style={{ fontSize: 10, color: m.txt, opacity: 0.7, marginTop: 2 }}>{count} {count === 1 ? "entry" : "entries"}</div>
                          </div>
                          <div style={{ fontSize: 16, color: m.txt, opacity: 0.5 }}>›</div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                      <button onClick={() => setMoodFilter(null)} style={{ fontSize: 11, color: C.teal, background: "none", border: "none", padding: 0, cursor: "pointer" }}>← all moods</button>
                      <span style={{ fontSize: 11, color: C.mid }}>· {moodFilter} entries</span>
                    </div>
                    <div style={{ display: "flex", gap: 6, marginBottom: 14, background: "#eee9e2", borderRadius: 10, padding: 3, overflowX: "auto" }}>
                      {entries.filter(e => e.tags?.includes(moodFilter)).map((en, i) => (
                        <button key={en.id} onClick={() => { setSel(entries.indexOf(en)); }} style={{ flex: "0 0 auto", padding: "7px 12px", fontSize: 11, fontWeight: 600, borderRadius: 8, background: entries[sel]?.id===en.id?"white":"transparent", color: entries[sel]?.id===en.id?C.tealDk:C.mid, border: "none", whiteSpace: "nowrap" }}>{fmt(en.entry_date)}</button>
                      ))}
                    </div>
                  </>
                )}
              </>
            )}

            {(view === "timeline" || moodFilter) && (
            <div style={{ display: "flex", gap: 6, marginBottom: 14, background: "#eee9e2", borderRadius: 10, padding: 3, overflowX: "auto" }}>
              {(view === "timeline" ? entries : entries.filter(e => e.tags?.includes(moodFilter))).slice(0, 4).map((en, i) => {
                const actualIdx = entries.indexOf(en);
                return <button key={en.id} onClick={() => setSel(actualIdx)} style={{ flex: "0 0 auto", padding: "7px 12px", fontSize: 11, fontWeight: 600, borderRadius: 8, background: sel===actualIdx?"white":"transparent", color: sel===actualIdx?C.tealDk:C.mid, border: "none", whiteSpace: "nowrap" }}>{fmt(en.entry_date)}</button>;
              })}
            </div>)}
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
            <ShareToComm entry={e} currentAiReply={currentAiReply} user={user} go={go} />
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

function CheersScreen({ go, user, cheers, setCheers }) {
  const [tab, setTab] = useState("received");
  const [sent, setSent] = useState([]);
  const [loadingSent, setLoadingSent] = useState(false);
  const [replyingTo, setReplyingTo] = useState(null);
  const [replyText, setReplyText] = useState("");
  const [sending, setSending] = useState(false);
  const [newType, setNewType] = useState("prompt");
  const [newMsg, setNewMsg] = useState("");
  const [newTo, setNewTo] = useState("");
  const [sendingNew, setSendingNew] = useState(false);
  const [sendErr, setSendErr] = useState("");
  const [sendDone, setSendDone] = useState(false);
  const [newPhotoFile, setNewPhotoFile] = useState(null);
  const [newPhotoUrl, setNewPhotoUrl] = useState("");
  const [voiceBlob, setVoiceBlob] = useState(null);
  const [voiceUrl, setVoiceUrl] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useState(null);
  const chunksRef = useState([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream);
      mediaRecorderRef[1](mr);
      chunksRef[1]([]);
      mr.ondataavailable = e => chunksRef[1](prev => [...prev, e.data]);
      mr.onstop = () => {
        const blob = new Blob(chunksRef[0], { type: "audio/webm" });
        setVoiceBlob(blob);
        setVoiceUrl(URL.createObjectURL(blob));
        stream.getTracks().forEach(t => t.stop());
      };
      mr.start();
      setIsRecording(true);
    } catch (e) { alert("Microphone access needed to record voice notes."); }
  };

  const stopRecording = () => {
    if (mediaRecorderRef[0] && isRecording) {
      mediaRecorderRef[0].stop();
      setIsRecording(false);
    }
  };

  const markRead = async id => {
    await supabase.from("cheers").update({ is_read: true }).eq("id", id);
    setCheers(c => c.map(x => x.id === id ? { ...x, is_read: true } : x));
  };

  useEffect(() => {
    if (tab === "sent") {
      setLoadingSent(true);
      supabase.from("cheers").select("*, profiles!cheers_to_user_id_fkey(username, display_name)").eq("from_user_id", user.id).order("created_at", { ascending: false })
        .then(({ data }) => { setSent(data || []); setLoadingSent(false); });
    }
  }, [tab, user.id]);

  const toggleLike = async (c) => {
    const newVal = !c.is_liked;
    await supabase.from("cheers").update({ is_liked: newVal }).eq("id", c.id);
    setCheers(prev => prev.map(x => x.id === c.id ? { ...x, is_liked: newVal } : x));
  };

  const sendReply = async (c) => {
    if (!replyText.trim()) return;
    setSending(true);
    await supabase.from("cheers").insert({ from_user_id: user.id, to_user_id: c.from_user_id, type: "prompt", content: replyText.trim(), reply_to: c.id, is_read: false });
    setReplyText(""); setReplyingTo(null); setSending(false);
  };

  const sendNew = async () => {
    if (!newTo.trim()) { setSendErr("Please enter a username"); return; }
    if (newType === "prompt" && !newMsg.trim()) { setSendErr("Please write a message"); return; }
    if (newType === "photo" && !newPhotoFile) { setSendErr("Please choose a photo"); return; }
    if (newType === "voice" && !voiceBlob) { setSendErr("Please record a voice note"); return; }
    setSendingNew(true); setSendErr("");
    const { data: profile } = await supabase.from("profiles").select("id").eq("username", newTo.trim()).single();
    if (!profile) { setSendErr("Username not found."); setSendingNew(false); return; }
    let mediaUrl = null;
    if (newType === "photo" && newPhotoFile) {
      const ext = newPhotoFile.name.split(".").pop();
      const path = `photos/${user.id}-${Date.now()}.${ext}`;
      const { error: upErr } = await supabase.storage.from("cheers-media").upload(path, newPhotoFile);
      if (upErr) { setSendErr("Could not upload photo."); setSendingNew(false); return; }
      const { data: urlData } = supabase.storage.from("cheers-media").getPublicUrl(path);
      mediaUrl = urlData.publicUrl;
    }
    if (newType === "voice" && voiceBlob) {
      const path = `voice/${user.id}-${Date.now()}.webm`;
      const { error: upErr } = await supabase.storage.from("cheers-media").upload(path, voiceBlob);
      if (upErr) { setSendErr("Could not upload voice note."); setSendingNew(false); return; }
      const { data: urlData } = supabase.storage.from("cheers-media").getPublicUrl(path);
      mediaUrl = urlData.publicUrl;
    }
    const { error } = await supabase.from("cheers").insert({ from_user_id: user.id, to_user_id: profile.id, type: newType, content: newType === "prompt" ? newMsg : (newMsg || ""), caption: mediaUrl });
    if (error) { setSendErr("Could not send. Try again."); setSendingNew(false); return; }
    setSendDone(true); setNewMsg(""); setNewTo(""); setNewPhotoFile(null); setNewPhotoUrl(""); setVoiceBlob(null); setVoiceUrl("");
    setTimeout(() => { setSendDone(false); setTab("sent"); }, 1500);
    setSendingNew(false);
  };

  const cheerCard = (c, isSent) => (
    <div key={c.id} className="card" style={{ borderColor: (!isSent && !c.is_read) ? "#F4C0D1" : "#e8e2da" }} onClick={() => !isSent && markRead(c.id)}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
        <div style={{ width: 34, height: 34, borderRadius: "50%", background: C.roseLt, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, fontWeight: 700, color: C.roseDk, flexShrink: 0 }}>
          {isSent ? "→" : "✦"}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: C.ink }}>
            {isSent ? `To: ${c.profiles?.username || c.profiles?.display_name || "Someone"}` : (c.reply_to ? "↩ Reply to your cheer" : `From: ${c.profiles?.username || c.profiles?.display_name || "A friend"}`)}
          </div>
          <div style={{ fontSize: 10, color: C.mid, marginTop: 1 }}>{c.type} · {new Date(c.created_at).toLocaleDateString("en-AU", { month: "short", day: "numeric" })}</div>
        </div>
        {!isSent && !c.is_read && <div style={{ width: 8, height: 8, borderRadius: "50%", background: C.rose }}></div>}
        {isSent && c.is_liked && <div style={{ fontSize: 14 }}>♥</div>}
      </div>
      {c.type === "prompt" && <div style={{ fontSize: 12, color: C.ink, lineHeight: 1.6, fontStyle: "italic" }}>"{c.content}"</div>}
      {c.type === "photo" && (c.caption ? <img src={c.caption} alt="cheer" style={{ width: "100%", borderRadius: 8, maxHeight: 180, objectFit: "cover", marginBottom: 6 }} /> : <div style={{ width: "100%", height: 80, background: C.tealLt, borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 32 }}>🖼</div>)}
      {c.type === "voice" && <div style={{ background: C.purpleLt, borderRadius: 9, padding: "9px 12px" }}>{c.caption ? <audio controls src={c.caption} style={{ width: "100%" }} /> : <div style={{ display: "flex", alignItems: "center", gap: 10 }}><div style={{ width: 28, height: 28, borderRadius: "50%", background: C.purpleDk, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, color: "white" }}>▶</div><div style={{ fontSize: 11, color: C.purpleDk, fontWeight: 600 }}>Voice note</div></div>}</div>}
      {!isSent && (
        <div style={{ display: "flex", gap: 6, marginTop: 10 }} onClick={ev => ev.stopPropagation()}>
          <button className={`tag${c.is_liked?" rz":""}`} style={{ fontSize: 11 }} onClick={() => toggleLike(c)}>{c.is_liked ? "♥ Loved" : "♡ Love this"}</button>
          <button className={`tag${replyingTo===c.id?" rz":""}`} style={{ fontSize: 11 }} onClick={() => { setReplyingTo(replyingTo===c.id?null:c.id); setReplyText(""); }}>↩ Reply</button>
        </div>
      )}
      {replyingTo === c.id && (
        <div style={{ marginTop: 10 }} onClick={ev => ev.stopPropagation()}>
          <textarea value={replyText} onChange={ev => setReplyText(ev.target.value)} placeholder="Write a reply..." className="ta" style={{ minHeight: 60, marginBottom: 8, fontSize: 12 }} />
          <div style={{ display: "flex", gap: 8 }}>
            <button className="pbtn" onClick={() => sendReply(c)} disabled={sending || !replyText.trim()} style={{ fontSize: 12, padding: "9px" }}>{sending ? "Sending..." : "Send reply"}</button>
            <button onClick={() => setReplyingTo(null)} style={{ flex: 1, padding: "9px", borderRadius: 10, border: ".5px solid #e0dbd4", background: "white", fontSize: 12, color: C.mid }}>Cancel</button>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="screen">
      <div className="hdr" style={{ background: C.roseDk }}>
        <div className="back" onClick={() => go("home")}>← home</div>
        <div className="htitle">Cheers</div>
        <div className="hsub">Send & receive encouragement</div>
      </div>
      <div className="body">
        <div style={{ display: "flex", gap: 0, background: "#eee9e2", borderRadius: 10, padding: 3, marginBottom: 14 }}>
          {[["received","Received"],["sent","Sent"],["send","Send new"]].map(([t,l]) => (
            <button key={t} onClick={() => setTab(t)} style={{ flex: 1, padding: "7px 0", fontSize: 11, fontWeight: 600, borderRadius: 8, background: tab===t?"white":"transparent", color: tab===t?C.roseDk:C.mid, border: "none" }}>{l}</button>
          ))}
        </div>

        {tab === "received" && (
          <>
            {cheers.length === 0 && <div className="card" style={{ textAlign: "center", padding: "32px 20px" }}><div style={{ fontSize: 32, marginBottom: 12 }}>✦</div><div style={{ fontSize: 14, fontWeight: 600, color: C.ink, marginBottom: 6 }}>No cheers yet</div><div style={{ fontSize: 12, color: C.mid }}>When friends send you encouragement it'll appear here.</div></div>}
            {cheers.map(c => cheerCard(c, false))}
          </>
        )}

        {tab === "sent" && (
          <>
            {loadingSent && <div style={{ textAlign: "center", padding: 20 }}><Spinner color={C.rose} /></div>}
            {!loadingSent && sent.length === 0 && <div className="card" style={{ textAlign: "center", padding: "32px 20px" }}><div style={{ fontSize: 32, marginBottom: 12 }}>✦</div><div style={{ fontSize: 14, fontWeight: 600, color: C.ink, marginBottom: 6 }}>No cheers sent yet</div><div style={{ fontSize: 12, color: C.mid }}>Tap "Send new" to encourage a friend!</div></div>}
            {sent.map(c => cheerCard(c, true))}
          </>
        )}

        {tab === "send" && (
          <div className="card">
            {sendErr && <div className="err">{sendErr}</div>}
            {sendDone && <div className="ok">✦ Cheer sent!</div>}
            <div className="slbl">Their username</div>
            <input className="inp" value={newTo} onChange={e => setNewTo(e.target.value)} placeholder="their_username" />
            <div style={{ display: "flex", gap: 0, background: "#eee9e2", borderRadius: 10, padding: 3, marginBottom: 12 }}>
              {[["prompt","✍ Message"],["photo","🖼 Photo"],["voice","🎙 Voice"]].map(([t,l]) => (
                <button key={t} onClick={() => setNewType(t)} style={{ flex: 1, padding: "7px 0", fontSize: 10, fontWeight: 600, borderRadius: 8, background: newType===t?"white":"transparent", color: newType===t?C.roseDk:C.mid, border: "none" }}>{l}</button>
              ))}
            </div>
            {newType === "prompt" && <textarea value={newMsg} onChange={e => setNewMsg(e.target.value)} placeholder="Write an encouraging message..." className="ta" style={{ minHeight: 90, marginBottom: 12 }} />}
            {newType === "photo" && (
              <div style={{ marginBottom: 12 }}>
                {newPhotoUrl ? (
                  <div style={{ position: "relative", marginBottom: 8 }}>
                    <img src={newPhotoUrl} alt="preview" style={{ width: "100%", borderRadius: 10, maxHeight: 200, objectFit: "cover" }} />
                    <button onClick={() => { setNewPhotoUrl(""); setNewPhotoFile(null); }} style={{ position: "absolute", top: 6, right: 6, background: "rgba(0,0,0,0.5)", color: "white", border: "none", borderRadius: "50%", width: 24, height: 24, fontSize: 12, cursor: "pointer" }}>✕</button>
                  </div>
                ) : (
                  <label style={{ display: "block", background: C.paper, border: "1.5px dashed #d0cac2", borderRadius: 12, padding: 24, textAlign: "center", cursor: "pointer", marginBottom: 8 }}>
                    <div style={{ fontSize: 28, marginBottom: 6 }}>🖼</div>
                    <div style={{ fontSize: 13, color: C.mid }}>Tap to choose a photo</div>
                    <input type="file" accept="image/*" style={{ display: "none" }} onChange={e => {
                      const file = e.target.files[0];
                      if (file) { setNewPhotoFile(file); setNewPhotoUrl(URL.createObjectURL(file)); }
                    }} />
                  </label>
                )}
                <textarea value={newMsg} onChange={e => setNewMsg(e.target.value)} placeholder="Add a caption..." className="ta" style={{ minHeight: 50 }} />
              </div>
            )}
            {newType === "voice" && (
              <div style={{ background: C.purpleLt, borderRadius: 12, padding: 16, textAlign: "center", marginBottom: 12 }}>
                {voiceBlob ? (
                  <div>
                    <audio controls src={voiceUrl} style={{ width: "100%", marginBottom: 10 }} />
                    <button onClick={() => { setVoiceBlob(null); setVoiceUrl(""); }} style={{ fontSize: 11, color: C.purpleDk, background: "none", border: "none", cursor: "pointer", textDecoration: "underline" }}>Record again</button>
                  </div>
                ) : (
                  <div>
                    <div
                      onMouseDown={startRecording} onMouseUp={stopRecording}
                      onTouchStart={startRecording} onTouchEnd={stopRecording}
                      style={{ width: 60, height: 60, borderRadius: "50%", background: isRecording ? C.rose : C.purpleDk, display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 10px", fontSize: 24, color: "white", cursor: "pointer", transition: "background .2s" }}>
                      🎙
                    </div>
                    <div style={{ fontSize: 13, color: C.purpleDk, fontWeight: 600 }}>{isRecording ? "Recording... release to stop" : "Hold to record"}</div>
                    <div style={{ fontSize: 11, color: C.purple, marginTop: 4 }}>Up to 60 seconds</div>
                  </div>
                )}
              </div>
            )}
            <button className="pbtn" onClick={sendNew} disabled={sendingNew || sendDone}>{sendingNew ? <><Spinner />&nbsp;Sending...</> : "Send cheer"}</button>
          </div>
        )}
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

function ShareToComm({ entry, currentAiReply, user, go }) {
  const [open, setOpen] = useState(false);
  const [inc, setInc] = useState({ entry: true, ai: true, self: false });
  const [anon, setAnon] = useState(false);
  const [sharing, setSharing] = useState(false);
  const [shared, setShared] = useState(false);

  const buildContent = () => {
    const parts = [];
    if (inc.entry && entry?.text) parts.push(`"${entry.text}"`);
    if (inc.ai && currentAiReply) parts.push(`Better You reflected: "${currentAiReply}"`);
    if (inc.self && entry?.self_reply) parts.push(`My response: "${entry.self_reply}"`);
    return parts.join("\n\n");
  };

  const share = async () => {
    const content = buildContent();
    if (!content) return;
    setSharing(true);
    await supabase.from("posts").insert({ user_id: user.id, content, entry_id: entry.id, is_anonymous: anon });
    setSharing(false); setShared(true); setOpen(false);
    setTimeout(() => setShared(false), 3000);
  };

  return (
    <>
      <div style={{ display: "flex", gap: 6, marginTop: 4 }}>
        <div onClick={() => setOpen(o => !o)} style={{ flex: 1, border: `.5px solid ${open?C.purple:"#e0dbd4"}`, borderRadius: 9, padding: "9px 8px", textAlign: "center", cursor: "pointer", background: open?C.purpleLt:"white", fontSize: 12, fontWeight: 600, color: open?C.purpleDk:C.mid }}>
          👥 Share to community
        </div>
        {shared && <div style={{ flex: 1, border: `.5px solid ${C.teal}`, borderRadius: 9, padding: "9px 8px", textAlign: "center", background: C.tealLt, fontSize: 12, fontWeight: 600, color: C.tealDk }}>✓ Shared!</div>}
      </div>
      {open && (
        <div style={{ background: C.purpleLt, borderRadius: 12, padding: "12px 14px", marginTop: 8, border: `.5px solid ${C.purple}` }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: C.purpleDk, marginBottom: 10 }}>Choose what to share</div>
          {[
            ["entry", "Your original entry", entry?.text],
            ["ai", "AI reflection", currentAiReply],
            ["self", "Your self-response", entry?.self_reply],
          ].map(([k, l, val]) => val ? (
            <div key={k} onClick={() => setInc(i => ({ ...i, [k]: !i[k] }))} style={{ display: "flex", alignItems: "flex-start", gap: 8, marginBottom: 8, cursor: "pointer" }}>
              <div style={{ width: 18, height: 18, borderRadius: 4, border: `1.5px solid ${inc[k]?C.purple:"#d0cac2"}`, background: inc[k]?C.purple:"white", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, color: "white", flexShrink: 0, marginTop: 1 }}>{inc[k]?"✓":""}</div>
              <div>
                <div style={{ fontSize: 11, fontWeight: 600, color: C.purpleDk }}>{l}</div>
                <div style={{ fontSize: 10, color: C.purpleDk, opacity: 0.7, lineHeight: 1.4 }}>{val.slice(0, 50)}{val.length > 50 ? "..." : ""}</div>
              </div>
            </div>
          ) : null)}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 8, paddingTop: 8, borderTop: `.5px solid ${C.purple}` }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, cursor: "pointer" }} onClick={() => setAnon(a => !a)}>
              <div style={{ width: 16, height: 16, borderRadius: 4, border: `1.5px solid ${anon?C.purple:"#d0cac2"}`, background: anon?C.purple:"white", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, color: "white" }}>{anon?"✓":""}</div>
              <span style={{ fontSize: 11, color: C.purpleDk }}>Post anonymously</span>
            </div>
            <button onClick={share} disabled={sharing || !buildContent()} className="pbtn" style={{ width: "auto", padding: "8px 16px", background: C.purpleDk, fontSize: 12 }}>
              {sharing ? <Spinner /> : "Share now"}
            </button>
          </div>
        </div>
      )}
    </>
  );
}


function CommunityScreen({ go, user }) {
  const [tab, setTab] = useState("feed");
  const [posts, setPosts] = useState([]);
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newPost, setNewPost] = useState("");
  const [anon, setAnon] = useState(false);
  const [posting, setPosting] = useState(false);
  const [commentingOn, setCommentingOn] = useState(null);
  const [commentText, setCommentText] = useState("");
  const [comments, setComments] = useState({});
  const [newGroup, setNewGroup] = useState("");
  const [creatingGroup, setCreatingGroup] = useState(false);
  const [myGroups, setMyGroups] = useState([]);

  const loadFeed = async () => {
    setLoading(true);
    const { data: { user } } = await supabase.auth.getUser();
    const { data } = await supabase.from("posts").select("*, profiles(username, display_name), post_likes(user_id)").order("created_at", { ascending: false }).limit(30);
    if (data) data.forEach(p => { p.user_liked = (p.post_likes || []).some(l => l.user_id === user?.id); });
    setPosts(data || []);
    setLoading(false);
  };

  const loadGroups = async () => {
    const { data } = await supabase.from("groups").select("*, group_members(count)").order("created_at", { ascending: false });
    setGroups(data || []);
    const { data: mine } = await supabase.from("group_members").select("group_id").eq("user_id", user.id);
    setMyGroups((mine || []).map(m => m.group_id));
  };

  useEffect(() => { loadFeed(); loadGroups(); }, []);

  const submitPost = async () => {
    if (!newPost.trim()) return;
    setPosting(true);
    await supabase.from("posts").insert({ user_id: user.id, content: newPost.trim(), is_anonymous: anon });
    setNewPost(""); setAnon(false);
    await loadFeed();
    setPosting(false);
  };

  const toggleLike = async (post) => {
    const liked = post.user_liked;
    setPosts(prev => prev.map(p => p.id === post.id ? {
      ...p, user_liked: !liked,
      likes_count: liked ? Math.max(0, p.likes_count - 1) : p.likes_count + 1
    } : p));
    if (liked) {
      await supabase.from("post_likes").delete().eq("post_id", post.id).eq("user_id", user.id);
      await supabase.from("posts").update({ likes_count: Math.max(0, post.likes_count - 1) }).eq("id", post.id);
    } else {
      await supabase.from("post_likes").insert({ post_id: post.id, user_id: user.id });
      await supabase.from("posts").update({ likes_count: post.likes_count + 1 }).eq("id", post.id);
    }
    await loadFeed();
  };

  const loadComments = async (postId) => {
    if (commentingOn === postId) { setCommentingOn(null); return; }
    const { data } = await supabase.from("post_comments").select("*, profiles(username, display_name)").eq("post_id", postId).order("created_at", { ascending: true });
    setComments(c => ({ ...c, [postId]: data || [] }));
    setCommentingOn(postId);
  };

  const submitComment = async (postId) => {
    if (!commentText.trim()) return;
    await supabase.from("post_comments").insert({ post_id: postId, user_id: user.id, content: commentText.trim(), is_anonymous: anon });
    await supabase.from("posts").update({ comments_count: (posts.find(p => p.id === postId)?.comments_count || 0) + 1 }).eq("id", postId);
    setCommentText("");
    await loadComments(postId);
    await loadFeed();
  };

  const joinGroup = async (groupId) => {
    if (myGroups.includes(groupId)) {
      await supabase.from("group_members").delete().eq("group_id", groupId).eq("user_id", user.id);
      setMyGroups(g => g.filter(x => x !== groupId));
    } else {
      await supabase.from("group_members").insert({ group_id: groupId, user_id: user.id });
      setMyGroups(g => [...g, groupId]);
    }
  };

  const createGroup = async () => {
    if (!newGroup.trim()) return;
    setCreatingGroup(true);
    await supabase.from("groups").insert({ name: newGroup.trim(), created_by: user.id });
    setNewGroup("");
    await loadGroups();
    setCreatingGroup(false);
  };

  const displayName = (post) => post.is_anonymous ? "Anonymous" : (post.profiles?.username || post.profiles?.display_name || "Someone");

  return (
    <div className="screen">
      <div className="hdr" style={{ background: C.purpleDk }}>
        <div className="back" onClick={() => go("home")}>← home</div>
        <div className="htitle">Community</div>
        <div className="hsub">Connect & support each other</div>
      </div>
      <div className="body">
        <div style={{ display: "flex", gap: 0, background: "#eee9e2", borderRadius: 10, padding: 3, marginBottom: 14 }}>
          {[["feed","Feed"],["groups","Groups"]].map(([t,l]) => (
            <button key={t} onClick={() => setTab(t)} style={{ flex: 1, padding: "8px 0", fontSize: 12, fontWeight: 600, borderRadius: 8, background: tab===t?"white":"transparent", color: tab===t?C.purpleDk:C.mid, border: "none" }}>{l}</button>
          ))}
        </div>

        {tab === "feed" && (
          <>
            <div className="card" style={{ marginBottom: 14 }}>
              <textarea value={newPost} onChange={e => setNewPost(e.target.value)} placeholder="Share something with the community..." className="ta" style={{ minHeight: 80, marginBottom: 10 }} />
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer" }} onClick={() => setAnon(a => !a)}>
                  <div style={{ width: 18, height: 18, borderRadius: 4, border: `1.5px solid ${anon?C.purple:"#d0cac2"}`, background: anon?C.purple:"white", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, color: "white" }}>{anon?"✓":""}</div>
                  <span style={{ fontSize: 11, color: C.mid }}>Post anonymously</span>
                </div>
                <button className="pbtn" onClick={submitPost} disabled={posting || !newPost.trim()} style={{ width: "auto", padding: "9px 18px", background: C.purpleDk, fontSize: 12 }}>
                  {posting ? <Spinner /> : "Post"}
                </button>
              </div>
            </div>

            {loading && <div style={{ textAlign: "center", padding: 20 }}><Spinner color={C.purple} /></div>}

            {posts.map(post => (
              <div key={post.id} className="card" style={{ marginBottom: 10 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                  <div style={{ width: 30, height: 30, borderRadius: "50%", background: C.purpleLt, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: 700, color: C.purpleDk, flexShrink: 0 }}>
                    {post.is_anonymous ? "?" : displayName(post)[0].toUpperCase()}
                  </div>
                  <div>
                    <div style={{ fontSize: 12, fontWeight: 600, color: C.ink }}>{displayName(post)}</div>
                    <div style={{ fontSize: 10, color: C.mid }}>{new Date(post.created_at).toLocaleDateString("en-AU", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}</div>
                  </div>
                </div>
                <div style={{ fontSize: 13, color: C.ink, lineHeight: 1.7, marginBottom: 10 }}>
                  {post.content.length > 180 && !post.expanded
                    ? <>{post.content.slice(0, 180)}... <span onClick={() => setPosts(prev => prev.map(p => p.id === post.id ? {...p, expanded: true} : p))} style={{ color: C.purple, cursor: "pointer", fontWeight: 600 }}>read more</span></>
                    : <>{post.content}{post.content.length > 180 && <> <span onClick={() => setPosts(prev => prev.map(p => p.id === post.id ? {...p, expanded: false} : p))} style={{ color: C.purple, cursor: "pointer", fontWeight: 600 }}>show less</span></>}</>
                  }
                </div>
                <div style={{ display: "flex", gap: 8, borderTop: ".5px solid #f0ebe4", paddingTop: 8 }}>
                  <button onClick={() => toggleLike(post)} className="tag" style={{ fontSize: 11, color: post.user_liked?C.rose:C.mid, borderColor: post.user_liked?"#F4C0D1":"#e0dbd4", background: post.user_liked?C.roseLt:"white" }}>
                    {post.user_liked ? "♥" : "♡"} {post.likes_count > 0 ? post.likes_count : ""} Like
                  </button>
                  <button onClick={() => loadComments(post.id)} className="tag" style={{ fontSize: 11 }}>
                    💬 {post.comments_count > 0 ? post.comments_count : ""} Comment
                  </button>
                </div>
                {commentingOn === post.id && (
                  <div style={{ marginTop: 10 }}>
                    {(comments[post.id] || []).map(c => (
                      <div key={c.id} style={{ display: "flex", gap: 8, marginBottom: 8, padding: "8px 10px", background: C.purpleLt, borderRadius: 10 }}>
                        <div style={{ width: 22, height: 22, borderRadius: "50%", background: C.purple, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, color: "white", flexShrink: 0 }}>
                          {c.is_anonymous ? "?" : (c.profiles?.username || "?")[0].toUpperCase()}
                        </div>
                        <div>
                          <div style={{ fontSize: 10, fontWeight: 600, color: C.purpleDk }}>{c.is_anonymous ? "Anonymous" : (c.profiles?.username || c.profiles?.display_name || "Someone")}</div>
                          <div style={{ fontSize: 12, color: C.ink, lineHeight: 1.5 }}>{c.content}</div>
                        </div>
                      </div>
                    ))}
                    <div style={{ display: "flex", gap: 8, marginTop: 6 }}>
                      <textarea value={commentText} onChange={e => setCommentText(e.target.value)} placeholder="Write a comment..." className="ta" style={{ flex: 1, minHeight: 40 }} />
                      <button onClick={() => submitComment(post.id)} className="pbtn" style={{ width: "auto", padding: "0 14px", background: C.purpleDk, fontSize: 12 }} disabled={!commentText.trim()}>Send</button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </>
        )}

        {tab === "groups" && (
          <>
            <div className="card" style={{ marginBottom: 14 }}>
              <div className="slbl">Create a group</div>
              <div style={{ display: "flex", gap: 8 }}>
                <input className="inp" value={newGroup} onChange={e => setNewGroup(e.target.value)} placeholder="Group name..." style={{ flex: 1, marginBottom: 0 }} />
                <button onClick={createGroup} className="pbtn" style={{ width: "auto", padding: "0 14px", background: C.purpleDk, fontSize: 12 }} disabled={creatingGroup || !newGroup.trim()}>
                  {creatingGroup ? <Spinner /> : "Create"}
                </button>
              </div>
            </div>
            {groups.map(g => (
              <div key={g.id} className="card" style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <div style={{ width: 40, height: 40, borderRadius: 11, background: C.purpleLt, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, flexShrink: 0 }}>👥</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: C.ink }}>{g.name}</div>
                  <div style={{ fontSize: 10, color: C.mid, marginTop: 1 }}>{g.group_members?.[0]?.count || 0} members</div>
                </div>
                <button onClick={() => joinGroup(g.id)} style={{ padding: "6px 12px", borderRadius: 20, fontSize: 11, fontWeight: 600, border: `1px solid ${myGroups.includes(g.id)?C.purple:"#e0dbd4"}`, background: myGroups.includes(g.id)?C.purpleLt:"white", color: myGroups.includes(g.id)?C.purpleDk:C.mid, cursor: "pointer" }}>
                  {myGroups.includes(g.id) ? "Joined ✓" : "Join"}
                </button>
              </div>
            ))}
            {groups.length === 0 && <div className="card" style={{ textAlign: "center", padding: "24px 16px", color: C.mid, fontSize: 13 }}>No groups yet — create the first one!</div>}
          </>
        )}
      </div>
      <Nav active="community" go={go} />
    </div>
  );
}

function CrisisScreen({ go, user }) {
  const [tab, setTab] = useState("breathe");
  const [breathPhase, setBreathPhase] = useState("inhale");
  const [breathCount, setBreathCount] = useState(4);
  const [groundStep, setGroundStep] = useState(0);
  const [country, setCountry] = useState("australia");
  const [emergencyContact, setEmergencyContact] = useState("");
  const [savingContact, setSavingContact] = useState(false);

  useEffect(() => {
    supabase.from("profiles").select("emergency_contact, country").eq("id", user.id).single()
      .then(({ data }) => {
        if (data?.emergency_contact) setEmergencyContact(data.emergency_contact);
        if (data?.country) setCountry(data.country);
      });
  }, [user.id]);

  useEffect(() => {
    if (tab !== "breathe") return;
    const phases = [
      { phase: "inhale", count: 4 },
      { phase: "hold", count: 4 },
      { phase: "exhale", count: 6 },
      { phase: "rest", count: 2 },
    ];
    let phaseIdx = 0;
    let count = phases[0].count;
    const interval = setInterval(() => {
      count--;
      setBreathCount(count);
      if (count <= 0) {
        phaseIdx = (phaseIdx + 1) % phases.length;
        count = phases[phaseIdx].count;
        setBreathPhase(phases[phaseIdx].phase);
        setBreathCount(count);
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [tab]);

  const groundSteps = [
    { num: 5, sense: "see", prompt: "Name 5 things you can SEE right now" },
    { num: 4, sense: "touch", prompt: "Name 4 things you can TOUCH" },
    { num: 3, sense: "hear", prompt: "Name 3 things you can HEAR" },
    { num: 2, sense: "smell", prompt: "Name 2 things you can SMELL" },
    { num: 1, sense: "taste", prompt: "Name 1 thing you can TASTE" },
  ];

  const helplines = {
    australia: [
      { name: "Lifeline", number: "13 11 14", desc: "24/7 crisis support" },
      { name: "Beyond Blue", number: "1300 22 4636", desc: "Anxiety & depression support" },
      { name: "Suicide Call Back Service", number: "1300 659 467", desc: "24/7 counselling" },
      { name: "Kids Helpline", number: "1800 55 1800", desc: "Ages 5-25, 24/7" },
    ],
    uk: [
      { name: "Samaritans", number: "116 123", desc: "24/7 emotional support" },
      { name: "Crisis Text Line", number: "Text HELLO to 85258", desc: "24/7 text support" },
      { name: "Mind", number: "0300 123 3393", desc: "Mental health support" },
    ],
    usa: [
      { name: "988 Suicide & Crisis Lifeline", number: "988", desc: "Call or text 988, 24/7" },
      { name: "Crisis Text Line", number: "Text HOME to 741741", desc: "24/7 text support" },
      { name: "NAMI Helpline", number: "1-800-950-6264", desc: "Mon-Fri 10am-10pm ET" },
    ],
    newzealand: [
      { name: "Lifeline", number: "0800 543 354", desc: "24/7 crisis support" },
      { name: "Youthline", number: "0800 376 633", desc: "Youth support 24/7" },
      { name: "1737", number: "1737", desc: "Call or text, 24/7" },
    ],
  };

  const phaseColors = { inhale: C.teal, hold: C.purple, exhale: C.rose, rest: C.mid };
  const phaseSize = { inhale: 130, hold: 130, exhale: 100, rest: 90 };

  const saveContact = async () => {
    setSavingContact(true);
    await supabase.from("profiles").update({ emergency_contact: emergencyContact, country }).eq("id", user.id);
    setSavingContact(false);
    alert("Saved!");
  };

  return (
    <div className="screen">
      <div className="hdr" style={{ background: "#1a1a2e", paddingTop: 52 }}>
        <div className="back" style={{ color: "rgba(255,255,255,0.5)" }} onClick={() => go("home")}>← home</div>
        <div className="htitle" style={{ color: "white" }}>I'm struggling</div>
        <div className="hsub" style={{ color: "rgba(255,255,255,0.5)" }}>You are not alone. Take a breath.</div>
      </div>
      <div className="body" style={{ paddingTop: 10 }}>
        <div style={{ display: "flex", gap: 0, background: "#eee9e2", borderRadius: 10, padding: 3, marginBottom: 16 }}>
          {[["breathe","Breathe"],["ground","Ground"],["helplines","Helplines"],["contact","My contact"]].map(([t,l]) => (
            <button key={t} onClick={() => setTab(t)} style={{ flex: 1, padding: "7px 0", fontSize: 10, fontWeight: 600, borderRadius: 8, background: tab===t?"white":"transparent", color: tab===t?"#1a1a2e":C.mid, border: "none" }}>{l}</button>
          ))}
        </div>

        {tab === "breathe" && (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "20px 0" }}>
            <div style={{ fontSize: 12, color: C.mid, marginBottom: 24, textAlign: "center", lineHeight: 1.6 }}>Follow the circle. Let it guide your breath.<br/>This will help calm your nervous system.</div>
            <div style={{
              width: phaseSize[breathPhase], height: phaseSize[breathPhase],
              borderRadius: "50%", background: phaseColors[breathPhase],
              display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
              transition: "width 1s ease, height 1s ease, background 1s ease",
              marginBottom: 20
            }}>
              <div style={{ fontSize: 11, color: "white", textTransform: "uppercase", letterSpacing: ".1em" }}>{breathPhase}</div>
              <div style={{ fontSize: 32, fontFamily: "'Playfair Display',serif", color: "white", fontWeight: 600 }}>{breathCount}</div>
            </div>
            <div style={{ fontSize: 12, color: C.mid, textAlign: "center" }}>Inhale 4 · Hold 4 · Exhale 6 · Rest 2</div>
          </div>
        )}

        {tab === "ground" && (
          <div>
            <div style={{ fontSize: 12, color: C.mid, marginBottom: 16, lineHeight: 1.6, textAlign: "center" }}>The 5-4-3-2-1 technique brings you back to the present moment.</div>
            {groundSteps.map((step, i) => (
              <div key={i} onClick={() => setGroundStep(i)} style={{ display: "flex", alignItems: "center", gap: 14, padding: "14px", background: groundStep===i?"#1a1a2e":C.paper, borderRadius: 12, marginBottom: 8, cursor: "pointer", border: `.5px solid ${groundStep===i?"#1a1a2e":"#e0dbd4"}`, transition: "all .2s" }}>
                <div style={{ width: 36, height: 36, borderRadius: "50%", background: groundStep===i?C.teal:C.tealLt, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, fontWeight: 700, color: groundStep===i?"white":C.tealDk, flexShrink: 0 }}>{step.num}</div>
                <div style={{ fontSize: 13, color: groundStep===i?"white":C.ink, lineHeight: 1.5 }}>{step.prompt}</div>
              </div>
            ))}
            <div style={{ marginTop: 8, padding: "12px 14px", background: C.tealLt, borderRadius: 12, fontSize: 12, color: C.tealDk, lineHeight: 1.6, textAlign: "center" }}>
              Take your time with each step. There is no rush.
            </div>
          </div>
        )}

        {tab === "helplines" && (
          <div>
            <div className="slbl">Select your country</div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6, marginBottom: 16 }}>
              {[["australia","🇦🇺 Australia"],["uk","🇬🇧 UK"],["usa","🇺🇸 USA"],["newzealand","🇳🇿 New Zealand"]].map(([c,l]) => (
                <button key={c} onClick={() => setCountry(c)} style={{ padding: "9px 8px", borderRadius: 10, fontSize: 11, fontWeight: 600, border: `1px solid ${country===c?"#1a1a2e":"#e0dbd4"}`, background: country===c?"#1a1a2e":"white", color: country===c?"white":C.mid, cursor: "pointer" }}>{l}</button>
              ))}
            </div>
            {(helplines[country] || []).map((h, i) => (
              <div key={i} className="card" style={{ marginBottom: 8 }}>
                <div style={{ fontSize: 13, fontWeight: 600, color: C.ink, marginBottom: 2 }}>{h.name}</div>
                <div style={{ fontSize: 11, color: C.mid, marginBottom: 8 }}>{h.desc}</div>
                <a href={`tel:${h.number.replace(/\s/g,"")}`} style={{ display: "block", background: "#1a1a2e", color: "white", borderRadius: 10, padding: "10px", textAlign: "center", fontSize: 14, fontWeight: 600, textDecoration: "none" }}>📞 {h.number}</a>
              </div>
            ))}
          </div>
        )}

        {tab === "contact" && (
          <div>
            <div style={{ fontSize: 13, color: C.ink, lineHeight: 1.7, marginBottom: 16 }}>Save a trusted person's number here. When you're struggling, you can call them directly from this screen.</div>
            <div className="slbl">Emergency contact phone number</div>
            <input className="inp" value={emergencyContact} onChange={e => setEmergencyContact(e.target.value)} placeholder="+61 400 000 000" type="tel" />
            <button className="pbtn" style={{ background: "#1a1a2e", marginBottom: 16 }} onClick={saveContact} disabled={savingContact}>
              {savingContact ? "Saving..." : "Save contact"}
            </button>
            {emergencyContact && (
              <a href={`tel:${emergencyContact.replace(/\s/g,"")}`} style={{ display: "block", background: C.teal, color: "white", borderRadius: 12, padding: "14px", textAlign: "center", fontSize: 15, fontWeight: 600, textDecoration: "none" }}>
                📞 Call {emergencyContact}
              </a>
            )}
            <div style={{ marginTop: 16, padding: "12px 14px", background: C.roseLt, borderRadius: 12, fontSize: 12, color: C.roseDk, lineHeight: 1.6 }}>
              If you are in immediate danger, please call emergency services — 000 in Australia, 999 in UK, 911 in USA.
            </div>
          </div>
        )}
      </div>
      <Nav active="home" go={go} />
    </div>
  );
}


function getAI_safe(text) { return getAI(text); }

function InsightsScreen({ go, user }) {
  const [entries, setEntries] = useState([]);
  const [moods, setMoods] = useState([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const weekDates = getWeekDates();
    Promise.all([
      supabase.from("entries").select("*").eq("user_id", user.id).gte("entry_date", weekDates[0]).lte("entry_date", weekDates[6]),
      supabase.from("mood_logs").select("*").eq("user_id", user.id).gte("log_date", weekDates[0]).lte("log_date", weekDates[6]),
    ]).then(([e, m]) => { setEntries(e.data || []); setMoods(m.data || []); setLoading(false); });
  }, [user.id]);
  const weekDates = getWeekDates();
  const DAY_LABELS = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
  const today = new Date().toISOString().split("T")[0];
  const todayIdx = weekDates.indexOf(today);
  const avgMood = moods.length ? (moods.reduce((a, m) => a + m.mood_score, 0) / moods.length).toFixed(1) : null;
  const totalWords = entries.reduce((a, e) => a + (e.text || "").split(/\s+/).filter(Boolean).length, 0);
  const topTag = (() => { const counts = {}; entries.flatMap(e => e.tags || []).forEach(t => { counts[t] = (counts[t] || 0) + 1; }); return Object.keys(counts).sort((a, b) => counts[b] - counts[a])[0] || null; })();
  const moodCounts = { Great: 0, Good: 0, Okay: 0, Low: 0, Hard: 0 };
  const moodMap = { 5: "Great", 4: "Good", 3: "Okay", 2: "Low", 1: "Hard" };
  moods.forEach(m => { if (moodMap[m.mood_score]) moodCounts[moodMap[m.mood_score]]++; });
  const moodColors = { Great: C.teal, Good: C.tealDk, Okay: C.amber, Low: C.rose, Hard: C.roseDk };
  const aiInsight = (() => {
    if (!moods.length && !entries.length) return "Start logging your mood and writing entries to see your weekly insights here.";
    if (avgMood >= 4) return "You had a strong week emotionally. Your consistency is building real self-awareness.";
    if (avgMood >= 3) return "A balanced week overall. Keep showing up — the habit is what matters most.";
    return "It looks like this was a harder week. That's okay — you showed up and that counts.";
  })();
  return (
    <div className="screen">
      <div className="hdr" style={{ background: C.tealDk, paddingTop: 52 }}>
        <div className="back" style={{ color: "rgba(255,255,255,.5)" }} onClick={() => go("home")}>← home</div>
        <div className="htitle">Weekly insights</div>
        <div className="hsub">Your mood & journal summary</div>
      </div>
      <div className="body">
        {loading ? <div style={{ textAlign: "center", padding: 40 }}><Spinner color={C.teal} /></div> : (
          <>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 14 }}>
              {[{ v: entries.length, l: "Entries this week" }, { v: avgMood || "—", l: "Avg mood score" }, { v: totalWords, l: "Words written" }, { v: topTag || "—", l: "Top mood tag" }].map((m, i) => (
                <div key={i} style={{ background: C.tealLt, borderRadius: 12, padding: 14 }}>
                  <div style={{ fontSize: 26, fontWeight: 700, color: C.tealDk }}>{m.v}</div>
                  <div style={{ fontSize: 11, color: C.teal, marginTop: 2 }}>{m.l}</div>
                </div>
              ))}
            </div>
            <div className="card" style={{ marginBottom: 12 }}>
              <div className="slbl" style={{ marginBottom: 10 }}>Mood this week</div>
              <div style={{ display: "flex", alignItems: "flex-end", gap: 6, height: 80 }}>
                {weekDates.map((d, i) => {
                  const mood = moods.find(m => m.log_date === d);
                  return (
                    <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                      <div style={{ width: "100%", height: mood ? `${(mood.mood_score / 5) * 64}px` : "6px", borderRadius: 6, background: i === todayIdx ? C.teal : mood ? C.tealDk : "#e8e2da", opacity: mood ? 1 : 0.35 }} />
                      <div style={{ fontSize: 9, color: i === todayIdx ? C.tealDk : C.mid, fontWeight: i === todayIdx ? 700 : 400 }}>{DAY_LABELS[i].charAt(0)}</div>
                    </div>
                  );
                })}
              </div>
            </div>
            <div className="card" style={{ marginBottom: 12 }}>
              <div className="slbl" style={{ marginBottom: 10 }}>Mood breakdown</div>
              {Object.entries(moodCounts).map(([label, count]) => {
                const pct = moods.length ? Math.round((count / moods.length) * 100) : 0;
                return (
                  <div key={label} style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
                    <div style={{ fontSize: 12, color: C.mid, width: 44 }}>{label}</div>
                    <div style={{ flex: 1, height: 6, background: "#e8e2da", borderRadius: 99, overflow: "hidden" }}>
                      <div style={{ width: `${pct}%`, height: "100%", background: moodColors[label], borderRadius: 99 }} />
                    </div>
                    <div style={{ fontSize: 11, color: C.mid, width: 28, textAlign: "right" }}>{pct}%</div>
                  </div>
                );
              })}
            </div>
            <div style={{ background: C.tealLt, borderRadius: 14, padding: "14px 16px", border: `.5px solid ${C.teal}`, marginBottom: 12 }}>
              <div style={{ fontSize: 9, textTransform: "uppercase", letterSpacing: ".08em", color: C.tealDk, fontWeight: 600, marginBottom: 6 }}>✦ This week's insight</div>
              <div style={{ fontSize: 13, color: C.tealDk, lineHeight: 1.7, fontStyle: "italic" }}>{aiInsight}</div>
            </div>
            {entries.length === 0 && (
              <div className="card" style={{ textAlign: "center", padding: "28px 20px" }}>
                <div style={{ fontSize: 32, marginBottom: 10 }}>✍️</div>
                <div style={{ fontSize: 14, fontWeight: 600, color: C.ink, marginBottom: 6 }}>No entries this week yet</div>
                <div style={{ fontSize: 12, color: C.mid, marginBottom: 14 }}>Write your first entry to start building insights.</div>
                <button className="pbtn" onClick={() => go("entry")}>Write now</button>
              </div>
            )}
          </>
        )}
      </div>
      <Nav active="home" go={go} />
    </div>
  );
}

function ProfileScreen({ go, user }) {
  const [entryCount, setEntryCount] = useState(0);
  const [streak, setStreak] = useState(0);
  const [totalMoods, setTotalMoods] = useState(0);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);
  const [showDelete, setShowDelete] = useState(false);
  const name = user?.user_metadata?.display_name || user?.email?.split("@")[0] || "there";
  const initials = name.slice(0, 2).toUpperCase();
  const joinDate = new Date(user?.created_at).toLocaleDateString("en-AU", { month: "long", year: "numeric" });
  useEffect(() => {
    const weekDates = getWeekDates();
    Promise.all([
      supabase.from("entries").select("id", { count: "exact" }).eq("user_id", user.id),
      supabase.from("mood_logs").select("log_date").eq("user_id", user.id).order("log_date", { ascending: false }).limit(60),
    ]).then(([e, m]) => {
      setEntryCount(e.count || 0);
      const dates = (m.data || []).map(d => d.log_date);
      setTotalMoods(dates.length);
      let count = 0;
      const check = new Date();
      if (!dates.includes(check.toISOString().split("T")[0])) check.setDate(check.getDate() - 1);
      while (true) {
        const s = check.toISOString().split("T")[0];
        if (dates.includes(s)) { count++; check.setDate(check.getDate() - 1); } else break;
      }
      setStreak(count);
      setLoading(false);
    });
  }, [user.id]);
  const deleteAccount = async () => {
    setDeleting(true);
    await supabase.from("entries").delete().eq("user_id", user.id);
    await supabase.from("mood_logs").delete().eq("user_id", user.id);
    await supabase.from("profiles").delete().eq("id", user.id);
    await supabase.auth.signOut();
  };
  return (
    <div className="screen">
      <div className="hdr" style={{ background: C.purpleDk, paddingTop: 52 }}>
        <div className="back" style={{ color: "rgba(255,255,255,.5)" }} onClick={() => go("home")}>← home</div>
        <div className="htitle">Profile</div>
        <div className="hsub">Your journey so far</div>
      </div>
      <div className="body">
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "24px 0 20px" }}>
          <div style={{ width: 72, height: 72, borderRadius: "50%", background: C.purpleLt, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 26, fontWeight: 700, color: C.purpleDk, marginBottom: 12 }}>{initials}</div>
          <div style={{ fontSize: 20, fontWeight: 700, color: C.ink }}>{name}</div>
          <div style={{ fontSize: 12, color: C.mid, marginTop: 2 }}>{user?.email}</div>
          <div style={{ fontSize: 11, color: C.mid, marginTop: 4 }}>Member since {joinDate}</div>
        </div>
        {loading ? <div style={{ textAlign: "center", padding: 20 }}><Spinner color={C.purple} /></div> : (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8, marginBottom: 16 }}>
            {[{ v: entryCount, l: "Entries" }, { v: `${streak}🔥`, l: "Day streak" }, { v: totalMoods, l: "Moods logged" }].map((s, i) => (
              <div key={i} style={{ background: C.purpleLt, borderRadius: 12, padding: "14px 10px", textAlign: "center" }}>
                <div style={{ fontSize: 22, fontWeight: 700, color: C.purpleDk }}>{s.v}</div>
                <div style={{ fontSize: 10, color: C.purple, marginTop: 2 }}>{s.l}</div>
              </div>
            ))}
          </div>
        )}
        <div className="card" style={{ marginBottom: 10 }}>
          {[
            { label: "My journal", action: () => go("reflect"), icon: "📖" },
            { label: "Weekly insights", action: () => go("insights"), icon: "📊" },
            { label: "Reminders", action: () => go("reminders"), icon: "🔔" },
            { label: "Privacy policy", action: () => go("privacy"), icon: "🔒" },
            { label: "Terms of service", action: () => go("terms"), icon: "📄" },
          ].map((item, i, arr) => (
            <div key={i} onClick={item.action} style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 0", borderBottom: i < arr.length - 1 ? `.5px solid #e8e2da` : "none", cursor: "pointer" }}>
              <span style={{ fontSize: 18 }}>{item.icon}</span>
              <div style={{ flex: 1, fontSize: 14, color: C.ink }}>{item.label}</div>
              <div style={{ color: "#c0b8ae", fontSize: 16 }}>›</div>
            </div>
          ))}
        </div>
        <button onClick={() => supabase.auth.signOut()} className="pbtn" style={{ background: C.mid, marginBottom: 10 }}>Sign out</button>
        {!showDelete ? (
          <div style={{ textAlign: "center" }}>
            <button onClick={() => setShowDelete(true)} style={{ background: "none", border: "none", fontSize: 12, color: C.mid, cursor: "pointer", textDecoration: "underline" }}>Delete my account</button>
          </div>
        ) : (
          <div style={{ background: "#FCEBEB", borderRadius: 12, padding: 16, border: ".5px solid #F09595" }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: "#A32D2D", marginBottom: 6 }}>Delete account?</div>
            <div style={{ fontSize: 12, color: "#A32D2D", marginBottom: 14, lineHeight: 1.6 }}>This will permanently delete all your entries, mood logs and account data. This cannot be undone.</div>
            <div style={{ display: "flex", gap: 8 }}>
              <button onClick={() => setShowDelete(false)} style={{ flex: 1, padding: "10px 0", borderRadius: 10, border: ".5px solid #e0dbd4", background: "white", fontSize: 13, color: C.mid, cursor: "pointer" }}>Cancel</button>
              <button onClick={deleteAccount} disabled={deleting} style={{ flex: 1, padding: "10px 0", borderRadius: 10, border: "none", background: "#A32D2D", color: "white", fontSize: 13, fontWeight: 600, cursor: "pointer" }}>{deleting ? "Deleting..." : "Yes, delete"}</button>
            </div>
          </div>
        )}
      </div>
      <Nav active="home" go={go} />
    </div>
  );
}

function PrivacyScreen({ go }) {
  return (
    <div className="screen">
      <div className="hdr" style={{ background: C.roseDk, paddingTop: 52 }}>
        <div className="back" style={{ color: "rgba(255,255,255,.5)" }} onClick={() => go("profile")}>← back</div>
        <div className="htitle">Privacy policy</div>
        <div className="hsub">Last updated March 2026</div>
      </div>
      <div className="body">
        {[
          { t: "Information we collect", b: "We collect your email address, journal entries, mood logs, and any content you choose to share with the community. We also collect usage data to improve the app." },
          { t: "How we use your information", b: "Your journal entries and mood data are used solely to provide you with AI reflections, insights, and a personalised experience. We never sell your data to third parties." },
          { t: "AI processing", b: "Your journal entries are sent to Anthropic's Claude AI to generate reflections and quotes. Your entries are not stored on Anthropic's servers beyond processing." },
          { t: "Data storage", b: "Your data is stored securely using Supabase, hosted on AWS. All data is encrypted in transit and at rest." },
          { t: "Data retention", b: "We retain your data for as long as your account is active. You can delete your account and all data at any time from the Profile screen." },
          { t: "Your rights", b: "You have the right to access, correct, or delete your personal data at any time. Contact us at privacy@betteryou.app." },
        ].map((s, i) => (
          <div key={i} className="card" style={{ marginBottom: 10 }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: C.ink, marginBottom: 6 }}>{s.t}</div>
            <div style={{ fontSize: 12, color: C.mid, lineHeight: 1.7 }}>{s.b}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function TermsScreen({ go }) {
  return (
    <div className="screen">
      <div className="hdr" style={{ background: C.roseDk, paddingTop: 52 }}>
        <div className="back" style={{ color: "rgba(255,255,255,.5)" }} onClick={() => go("profile")}>← back</div>
        <div className="htitle">Terms of service</div>
        <div className="hsub">Last updated March 2026</div>
      </div>
      <div className="body">
        {[
          { t: "Acceptance of terms", b: "By using BetterYou, you agree to these terms. If you do not agree, please do not use the app." },
          { t: "Not a medical service", b: "BetterYou is a wellness and journaling app, not a medical or mental health service. AI reflections are not a substitute for professional advice. If you are in crisis, please use the helplines in the app." },
          { t: "User responsibilities", b: "You must be 13 or older to use BetterYou. You agree not to post harmful, abusive, or illegal content." },
          { t: "Community guidelines", b: "The community feed is a safe, supportive space. Harassment or hate speech is prohibited and will result in account termination." },
          { t: "Account termination", b: "We reserve the right to terminate accounts that violate these terms. You may delete your account at any time from the Profile screen." },
          { t: "Contact", b: "For questions about these terms, contact us at legal@betteryou.app." },
        ].map((s, i) => (
          <div key={i} className="card" style={{ marginBottom: 10 }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: C.ink, marginBottom: 6 }}>{s.t}</div>
            <div style={{ fontSize: 12, color: C.mid, lineHeight: 1.7 }}>{s.b}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function OnboardingScreen({ user, onDone }) {
  const [step, setStep] = useState(0);
  const [name, setName] = useState(user?.user_metadata?.display_name || user?.email?.split("@")[0] || "");
  const [username, setUsername] = useState("");
  const [usernameErr, setUsernameErr] = useState("");
  const [saving, setSaving] = useState(false);
  return (
    <div className="screen" style={{ background: C.roseDk }}>
      {step > 0 && (
        <div style={{ padding: "52px 20px 0", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <button onClick={() => setStep(s => s - 1)} style={{ background: "none", border: "none", color: "rgba(255,255,255,.5)", fontSize: 13, cursor: "pointer" }}>← back</button>
          <div style={{ display: "flex", gap: 6 }}>
            {[1,2,3].map(i => (<div key={i} style={{ width: i <= step ? 20 : 6, height: 6, borderRadius: 99, background: i <= step ? "white" : "rgba(255,255,255,.25)", transition: "width .3s" }} />))}
          </div>
        </div>
      )}
      {step === 0 && (
        <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "40px 28px", textAlign: "center" }}>
          <div style={{ fontFamily: "'Playfair Display',serif", fontSize: 52, color: "white", fontWeight: 600, lineHeight: 1.1, marginBottom: 16 }}>Better<br/><em style={{ color: "#F4C0D1" }}>You</em></div>
          <div style={{ fontSize: 14, color: "rgba(255,255,255,.65)", lineHeight: 1.7, marginBottom: 48 }}>A safe space to reflect, grow, and feel supported every day.</div>
          <button className="pbtn" onClick={() => setStep(1)} style={{ background: "white", color: C.roseDk, fontSize: 15, padding: "14px 0" }}>Get started</button>
        </div>
      )}
      {step === 1 && (
        <div style={{ flex: 1, display: "flex", flexDirection: "column", padding: "24px 28px 40px" }}>
          <div style={{ fontSize: 11, color: "rgba(255,255,255,.5)", marginBottom: 8 }}>Step 1 of 3</div>
          <div style={{ fontFamily: "'Playfair Display',serif", fontSize: 28, color: "white", fontWeight: 600, marginBottom: 8 }}>What should we call you?</div>
          <div style={{ fontSize: 13, color: "rgba(255,255,255,.6)", marginBottom: 32, lineHeight: 1.6 }}>This is how we'll greet you each day.</div>
          <input value={name} onChange={e => setName(e.target.value)} placeholder="Your name" style={{ width: "100%", padding: "14px 16px", borderRadius: 12, border: "none", background: "rgba(255,255,255,.15)", color: "white", fontSize: 16, marginBottom: 16, outline: "none" }} />
          <button className="pbtn" onClick={() => name.trim() && setStep(2)} disabled={!name.trim()} style={{ background: "white", color: C.roseDk, fontSize: 15, padding: "14px 0", marginTop: "auto" }}>Continue</button>
        </div>
      )}
      {step === 2 && (
        <div style={{ flex: 1, display: "flex", flexDirection: "column", padding: "24px 28px 40px" }}>
          <div style={{ fontSize: 11, color: "rgba(255,255,255,.5)", marginBottom: 8 }}>Step 2 of 3</div>
          <div style={{ fontFamily: "'Playfair Display',serif", fontSize: 28, color: "white", fontWeight: 600, marginBottom: 8 }}>Choose a username</div>
          <div style={{ fontSize: 13, color: "rgba(255,255,255,.6)", marginBottom: 32, lineHeight: 1.6 }}>Friends use this to send you cheers.</div>
          {usernameErr && <div style={{ background: "rgba(255,255,255,.15)", borderRadius: 10, padding: "10px 14px", fontSize: 12, color: "white", marginBottom: 12 }}>{usernameErr}</div>}
          <input value={username} onChange={e => { setUsername(e.target.value.toLowerCase().replace(/\s/g,"_").replace(/[^a-z0-9_]/g,"")); setUsernameErr(""); }} placeholder="your_username" style={{ width: "100%", padding: "14px 16px", borderRadius: 12, border: "none", background: "rgba(255,255,255,.15)", color: "white", fontSize: 16, marginBottom: 8, outline: "none" }} />
          <div style={{ fontSize: 11, color: "rgba(255,255,255,.4)", marginBottom: 16 }}>Lowercase, numbers and underscores only</div>
          <button className="pbtn" onClick={async () => {
            if (!username.trim()) return;
            setSaving(true); setUsernameErr("");
            const { data: existing } = await supabase.from("profiles").select("id").eq("username", username.trim()).single();
            if (existing) { setUsernameErr("That username is taken — try another!"); setSaving(false); return; }
            setStep(3); setSaving(false);
          }} disabled={!username.trim() || saving} style={{ background: "white", color: C.roseDk, fontSize: 15, padding: "14px 0", marginTop: "auto" }}>{saving ? "Checking..." : "Continue"}</button>
        </div>
      )}
      {step === 3 && (
        <div style={{ flex: 1, display: "flex", flexDirection: "column", padding: "24px 28px 40px" }}>
          <div style={{ fontSize: 11, color: "rgba(255,255,255,.5)", marginBottom: 8 }}>Step 3 of 3</div>
          <div style={{ fontFamily: "'Playfair Display',serif", fontSize: 28, color: "white", fontWeight: 600, marginBottom: 24 }}>Here's what awaits you</div>
          {[
            { ic: "✍️", t: "Journal", s: "Write how you feel, any time" },
            { ic: "💬", t: "AI reflection", s: "Get a thoughtful response to every entry" },
            { ic: "📊", t: "Mood tracking", s: "See your emotional patterns over time" },
            { ic: "👥", t: "Community", s: "Share and support others anonymously" },
            { ic: "🆘", t: "Crisis support", s: "Breathing, grounding & helplines always available" },
          ].map((f, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 16 }}>
              <div style={{ width: 40, height: 40, borderRadius: 11, background: "rgba(255,255,255,.15)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, flexShrink: 0 }}>{f.ic}</div>
              <div>
                <div style={{ fontSize: 13, fontWeight: 600, color: "white" }}>{f.t}</div>
                <div style={{ fontSize: 11, color: "rgba(255,255,255,.55)", marginTop: 1 }}>{f.s}</div>
              </div>
            </div>
          ))}
          <button className="pbtn" onClick={async () => {
            setSaving(true);
            await supabase.from("profiles").update({ username: username.trim(), display_name: name.trim(), has_onboarded: true }).eq("id", user.id);
            await supabase.auth.updateUser({ data: { display_name: name.trim() } });
            setSaving(false); onDone();
          }} disabled={saving} style={{ background: "white", color: C.roseDk, fontSize: 15, padding: "14px 0", marginTop: "auto" }}>{saving ? "Setting up..." : "Let's go ✦"}</button>
        </div>
      )}
    </div>
  );
}


export default function App() {
  const [session, setSession] = useState(undefined);
  const [screen, setScreen] = useState("home");
  const [cheers, setCheers] = useState([]);
  const [rk, setRk] = useState(0);
  const [needsOnboarding, setNeedsOnboarding] = useState(false);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => setSession(session));
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_, s) => {
      setSession(s);
      if (s) {
        loadCheers(s.user.id);
        registerPush(s.user.id);
        supabase.from("profiles").select("has_onboarded").eq("id", s.user.id).single()
          .then(({ data }) => { if (!data?.has_onboarded) setNeedsOnboarding(true); });
      }
    });
    return () => subscription.unsubscribe();
  }, []);

  const registerPush = async (userId) => {
    try {
      if (!("Notification" in window) || !("serviceWorker" in navigator)) return;
      const permission = await Notification.requestPermission();
      if (permission !== "granted") return;
      const reg = await navigator.serviceWorker.ready;
      const VAPID_PUBLIC = "BEa9hgnpolYA0W-9vWgfR5aKkBpO5tT0y1I6dsAoHVeNHPWeqVhRbuDbDejV_BfxlOCrJo5ghzG1FZe_8TK188M";
      const sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: VAPID_PUBLIC
      });
      await supabase.from("push_subscriptions").upsert({ user_id: userId, subscription: sub.toJSON() });
    } catch (e) { console.log("Push setup failed:", e); }
  };

  const loadCheers = async uid => {
    const { data } = await supabase.from("cheers").select("*, profiles!cheers_from_user_id_fkey(username, display_name)").eq("to_user_id", uid).order("created_at", { ascending: false });
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
  if (needsOnboarding) return <><style>{css}</style><div className="phone"><OnboardingScreen user={session.user} onDone={() => setNeedsOnboarding(false)} /></div></>;

  const u = session.user;
  return (
    <>
      <style>{css}</style>
      <div className="phone">
        {screen === "home"      && <HomeScreen go={go} user={u} cheers={cheers} />}
        {screen === "entry"     && <EntryScreen go={go} user={u} onSave={onSave} />}
        {screen === "reflect"   && <ReflectScreen go={go} user={u} rk={rk} />}
        {screen === "share"     && <ShareScreen go={go} user={u} />}
        {screen === "cheers"    && <CheersScreen go={go} user={u} cheers={cheers} setCheers={setCheers} />}
        {screen === "sendCheer" && <SendCheerScreen go={go} user={u} />}
        {screen === "reminders" && <RemindersScreen go={go} user={u} />}
        {screen === "crisis"    && <CrisisScreen go={go} user={u} />}
        {screen === "community" && <CommunityScreen go={go} user={u} />}
        {screen === "insights"  && <InsightsScreen go={go} user={u} />}
        {screen === "profile"   && <ProfileScreen go={go} user={u} />}
        {screen === "privacy"   && <PrivacyScreen go={go} />}
        {screen === "terms"     && <TermsScreen go={go} />}
      </div>
    </>
  );
}
