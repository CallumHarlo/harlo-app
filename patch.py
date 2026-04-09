import re

path = '/Users/callumbenson/Downloads/betteryou/src/App.js'

with open(path, 'r') as f:
    content = f.read()

new_home = r'''function HomeScreen({ go, user, cheers }) {
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

  const getWeekDates = () => {
    const d = new Date();
    const diff = (d.getDay() + 6) % 7;
    return Array.from({ length: 7 }, (_, i) => {
      const date = new Date(d);
      date.setDate(d.getDate() - diff + i);
      return date.toISOString().split("T")[0];
    });
  };

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
            <div style={{ fontSize: 11, color: "rgba(255,255,255,.45)", marginTop: 2 }}>
              {new Date().toLocaleDateString("en-AU", { weekday: "long", month: "long", day: "numeric" })}
            </div>
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
            <div style={{ fontSize: 13, color: "#3C3489", lineHeight: 1.7, fontStyle: "italic" }}>{quote}</div>
          </div>
        )}
        <div onClick={() => supabase.auth.signOut()} style={{ textAlign: "center", fontSize: 11, color: C.mid, marginTop: 20, cursor: "pointer", padding: "8px 0" }}>Sign out</div>
      </div>
      <Nav active="home" go={go} />
    </div>
  );
}'''

pattern = re.compile(r'function HomeScreen\(\{ go, user, cheers \}\).*?(?=\nfunction EntryScreen)', re.DOTALL)

if not pattern.search(content):
    print("ERROR: Could not find HomeScreen function")
else:
    new_content = pattern.sub(new_home + '\n\n', content)
    with open(path, 'w') as f:
        f.write(new_content)
    print("SUCCESS: HomeScreen updated!")
