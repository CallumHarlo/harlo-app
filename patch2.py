import re

path = '/Users/callumbenson/Downloads/betteryou/src/App.js'

with open(path, 'r') as f:
    content = f.read()

# ── 1. FORGOT PASSWORD: add to AuthScreen ──────────────────────────────────
old_auth_btn = '''        <button className="pbtn" onClick={submit} disabled={load}>
          {load ? <><Spinner />&nbsp;{mode==="login"?"Signing in...":"Creating account..."}</> : mode==="login"?"Sign in":"Create account"}
        </button>'''

new_auth_btn = '''        <button className="pbtn" onClick={submit} disabled={load}>
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
        )}'''

# ── 2. WEEKLY INSIGHTS SCREEN ──────────────────────────────────────────────
insights_screen = r'''
function InsightsScreen({ go, user }) {
  const [entries, setEntries] = useState([]);
  const [moods, setMoods] = useState([]);
  const [loading, setLoading] = useState(true);

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
    Promise.all([
      supabase.from("entries").select("*").eq("user_id", user.id).gte("entry_date", weekDates[0]).lte("entry_date", weekDates[6]),
      supabase.from("mood_logs").select("*").eq("user_id", user.id).gte("log_date", weekDates[0]).lte("log_date", weekDates[6]),
    ]).then(([e, m]) => {
      setEntries(e.data || []);
      setMoods(m.data || []);
      setLoading(false);
    });
  }, [user.id]);

  const weekDates = getWeekDates();
  const DAY_LABELS = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
  const today = new Date().toISOString().split("T")[0];
  const todayIdx = weekDates.indexOf(today);

  const avgMood = moods.length ? (moods.reduce((a, m) => a + m.mood_score, 0) / moods.length).toFixed(1) : null;
  const totalWords = entries.reduce((a, e) => a + (e.text || "").split(/\s+/).filter(Boolean).length, 0);
  const topTag = (() => {
    const counts = {};
    entries.flatMap(e => e.tags || []).forEach(t => { counts[t] = (counts[t] || 0) + 1; });
    return Object.keys(counts).sort((a, b) => counts[b] - counts[a])[0] || null;
  })();

  const moodCounts = { Great: 0, Good: 0, Okay: 0, Low: 0, Hard: 0 };
  const moodMap = { 5: "Great", 4: "Good", 3: "Okay", 2: "Low", 1: "Hard" };
  moods.forEach(m => { if (moodMap[m.mood_score]) moodCounts[moodMap[m.mood_score]]++; });
  const moodColors = { Great: C.teal, Good: C.tealDk, Okay: C.amber, Low: C.rose, Hard: C.roseDk };

  const aiInsight = (() => {
    if (!moods.length && !entries.length) return "Start logging your mood and writing entries to see your weekly insights here.";
    if (avgMood >= 4) return "You had a strong week emotionally. Your consistency is building real self-awareness.";
    if (avgMood >= 3) return "A balanced week overall. Keep showing up — the habit is what matters most.";
    if (avgMood < 3 && moods.length > 0) return "It looks like this was a harder week. That's okay — you showed up and that counts.";
    return "Keep logging your mood each day to start seeing patterns emerge.";
  })();

  return (
    <div className="screen">
      <div className="hdr" style={{ background: C.tealDk, paddingTop: 52 }}>
        <div className="back" style={{ color: "rgba(255,255,255,.5)" }} onClick={() => go("home")}>← home</div>
        <div className="htitle">Weekly insights</div>
        <div className="hsub">Your mood & journal summary</div>
      </div>
      <div className="body">
        {loading ? (
          <div style={{ textAlign: "center", padding: 40 }}><Spinner color={C.teal} /></div>
        ) : (
          <>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 14 }}>
              {[
                { v: entries.length, l: "Entries this week" },
                { v: avgMood || "—", l: "Avg mood score" },
                { v: totalWords, l: "Words written" },
                { v: topTag || "—", l: "Top mood tag" },
              ].map((m, i) => (
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
                      <div style={{ width: "100%", height: mood ? `${(mood.mood_score / 5) * 64}px` : "6px", borderRadius: 6, background: i === todayIdx ? C.teal : mood ? C.tealDk : "#e8e2da", opacity: mood ? 1 : 0.35, transition: "height .4s ease" }} />
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
                      <div style={{ width: `${pct}%`, height: "100%", background: moodColors[label], borderRadius: 99, transition: "width .5s ease" }} />
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
'''

# ── 3. PROFILE SCREEN ──────────────────────────────────────────────────────
profile_screen = r'''
function ProfileScreen({ go, user }) {
  const [entries, setEntries] = useState([]);
  const [streak, setStreak] = useState(0);
  const [totalMoods, setTotalMoods] = useState(0);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);
  const [showDelete, setShowDelete] = useState(false);
  const name = user?.user_metadata?.display_name || user?.email?.split("@")[0] || "there";
  const initials = name.slice(0, 2).toUpperCase();
  const joinDate = new Date(user?.created_at).toLocaleDateString("en-AU", { month: "long", year: "numeric" });

  useEffect(() => {
    Promise.all([
      supabase.from("entries").select("id", { count: "exact" }).eq("user_id", user.id),
      supabase.from("mood_logs").select("log_date").eq("user_id", user.id).order("log_date", { ascending: false }).limit(60),
    ]).then(([e, m]) => {
      setEntries(e.count || 0);
      const dates = (m.data || []).map(d => d.log_date);
      setTotalMoods(dates.length);
      let count = 0;
      const check = new Date();
      const todayStr = check.toISOString().split("T")[0];
      if (!dates.includes(todayStr)) check.setDate(check.getDate() - 1);
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

        {loading ? (
          <div style={{ textAlign: "center", padding: 20 }}><Spinner color={C.purple} /></div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8, marginBottom: 16 }}>
            {[
              { v: entries, l: "Entries", ic: "✍️" },
              { v: `${streak}🔥`, l: "Day streak", ic: "" },
              { v: totalMoods, l: "Moods logged", ic: "😊" },
            ].map((s, i) => (
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
          ].map((item, i) => (
            <div key={i} onClick={item.action} style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 0", borderBottom: i < 2 ? `.5px solid #e8e2da` : "none", cursor: "pointer" }}>
              <span style={{ fontSize: 18 }}>{item.icon}</span>
              <div style={{ flex: 1, fontSize: 14, color: C.ink }}>{item.label}</div>
              <div style={{ color: "#c0b8ae", fontSize: 16 }}>›</div>
            </div>
          ))}
        </div>

        <button onClick={() => supabase.auth.signOut()} className="pbtn" style={{ background: C.mid, marginBottom: 10 }}>Sign out</button>

        {!showDelete ? (
          <div style={{ textAlign: "center" }}>
            <button onClick={() => setShowDelete(true)} style={{ background: "none", border: "none", fontSize: 12, color: "#e8e2da", cursor: "pointer", textDecoration: "underline" }}>Delete my account</button>
          </div>
        ) : (
          <div style={{ background: "#FCEBEB", borderRadius: 12, padding: 16, border: ".5px solid #F09595" }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: "#A32D2D", marginBottom: 6 }}>Delete account?</div>
            <div style={{ fontSize: 12, color: "#A32D2D", marginBottom: 14, lineHeight: 1.6 }}>This will permanently delete all your entries, mood logs and account data. This cannot be undone.</div>
            <div style={{ display: "flex", gap: 8 }}>
              <button onClick={() => setShowDelete(false)} style={{ flex: 1, padding: "10px 0", borderRadius: 10, border: ".5px solid #e0dbd4", background: "white", fontSize: 13, color: C.mid, cursor: "pointer" }}>Cancel</button>
              <button onClick={deleteAccount} disabled={deleting} style={{ flex: 1, padding: "10px 0", borderRadius: 10, border: "none", background: "#A32D2D", color: "white", fontSize: 13, fontWeight: 600, cursor: "pointer" }}>
                {deleting ? "Deleting..." : "Yes, delete"}
              </button>
            </div>
          </div>
        )}
      </div>
      <Nav active="home" go={go} />
    </div>
  );
}
'''

# ── 4. WIRE UP: add screens + nav + profile link in settings ───────────────
old_nav = '''[["home","home","🏠"],["write","entry","✍️"],["reflect","reflect","💬"],["community","community","👥"],["settings","reminders","⚙️"]]'''
new_nav = '''[["home","home","🏠"],["write","entry","✍️"],["reflect","reflect","💬"],["community","community","👥"],["settings","profile","⚙️"]]'''

old_screens = '''{screen === "home"      && <HomeScreen go={go} user={u} cheers={cheers} />}'''
new_screens = '''{screen === "home"      && <HomeScreen go={go} user={u} cheers={cheers} />}
        {screen === "insights"  && <InsightsScreen go={go} user={u} />}
        {screen === "profile"   && <ProfileScreen go={go} user={u} />}'''

# Apply all patches
result = content

if old_auth_btn in result:
    result = result.replace(old_auth_btn, new_auth_btn)
    print("✓ Forgot password added")
else:
    print("✗ Could not find auth button - skipping")

# Insert InsightsScreen and ProfileScreen before the last export/App function
insert_marker = '\nfunction SendCheerScreen'
if insert_marker in result:
    result = result.replace(insert_marker, insights_screen + profile_screen + insert_marker)
    print("✓ InsightsScreen + ProfileScreen added")
else:
    print("✗ Could not find insertion point")

if old_nav in result:
    result = result.replace(old_nav, new_nav)
    print("✓ Nav updated to profile")
else:
    print("✗ Could not find nav")

if old_screens in result:
    result = result.replace(old_screens, new_screens)
    print("✓ Screens wired up")
else:
    print("✗ Could not find screen router")

with open(path, 'w') as f:
    f.write(result)

print("\nDone! Check above for any skipped steps.")
