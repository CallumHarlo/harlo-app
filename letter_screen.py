c = open('src/App.js').read()

letter = """
function LetterScreen({ go, user }) {
  const [tab, setTab] = useState('write');
  const [content, setContent] = useState('');
  const [deliverDays, setDeliverDays] = useState(7);
  const [sending, setSending] = useState(false);
  const [done, setDone] = useState(false);
  const [letters, setLetters] = useState([]);
  const [loading, setLoading] = useState(false);
  const [openLetter, setOpenLetter] = useState(null);

  useEffect(() => {
    if (tab === 'inbox') {
      setLoading(true);
      supabase.from('letters_to_self').select('*').eq('user_id', user.id).order('created_at', { ascending: false })
        .then(({ data }) => { setLetters(data || []); setLoading(false); });
    }
  }, [tab, user.id]);

  const send = async () => {
    if (!content.trim()) return;
    setSending(true);
    const deliver_at = new Date(Date.now() + deliverDays * 86400000).toISOString();
    await supabase.from('letters_to_self').insert({ user_id: user.id, content: content.trim(), deliver_at, delivered: false });
    setSending(false);
    setDone(true);
    setContent('');
    setTimeout(() => { setDone(false); setTab('inbox'); }, 2000);
  };

  const isReady = (l) => new Date(l.deliver_at) <= new Date();

  return (
    <div className="screen">
      <div className="hdr" style={{ background:'#1a2a1a' }}>
        <div className="back" onClick={() => go('home')}>back</div>
        <div className="htitle" style={{ fontFamily:"'Playfair Display',serif" }}>Letters to Yourself</div>
        <div className="hsub">Words from you, to you</div>
      </div>
      <div className="body">
        <div style={{ display:'flex', gap:0, background:'#eee9e2', borderRadius:10, padding:3, marginBottom:14 }}>
          {[['write','Write a letter'],['inbox','My letters']].map(([t,l]) => (
            <button key={t} onClick={() => setTab(t)} style={{ flex:1, padding:'7px 0', fontSize:12, fontWeight:600, borderRadius:8, background:tab===t?'white':'transparent', color:tab===t?'#1a2a1a':'#888', border:'none' }}>{l}</button>
          ))}
        </div>

        {tab === 'write' && (
          <div>
            <div className="card" style={{ marginBottom:12, background:'#f0f7f0', border:'1px solid #c8e0c8' }}>
              <div style={{ fontSize:12, color:'#2D5A4F', fontWeight:600, marginBottom:4 }}>Dear future me...</div>
              <div style={{ fontSize:11, color:'#4A7C6F', lineHeight:1.6 }}>Write to yourself from where you are right now. Your future self will read this when the time comes.</div>
            </div>
            {done && <div className="ok" style={{ marginBottom:12 }}>Letter sealed. Your future self will read this soon. 🌿</div>}
            <div className="slbl">Your letter</div>
            <textarea value={content} onChange={e => setContent(e.target.value)} className="ta" style={{ minHeight:200, marginBottom:16, fontFamily:"'Playfair Display',serif", fontSize:14, fontStyle:'italic', lineHeight:1.8 }} placeholder="Dear future me, right now I'm feeling..." />
            <div className="slbl">Deliver in</div>
            <div style={{ display:'flex', gap:8, marginBottom:16, flexWrap:'wrap' }}>
              {[3,7,14,30].map(d => (
                <button key={d} onClick={() => setDeliverDays(d)} style={{ flex:1, minWidth:60, padding:'8px 0', borderRadius:10, border:deliverDays===d?'2px solid #2D5A4F':'1px solid #e0dbd4', background:deliverDays===d?'#2D5A4F':'white', color:deliverDays===d?'white':'#666', fontSize:12, fontWeight:600 }}>{d} days</button>
              ))}
            </div>
            <div style={{ fontSize:11, color:'#888', textAlign:'center', marginBottom:16 }}>This letter will be waiting for you on {new Date(Date.now() + deliverDays * 86400000).toLocaleDateString('en-AU', { weekday:'long', day:'numeric', month:'long' })}</div>
            <button className="pbtn" onClick={send} disabled={sending || done || !content.trim()} style={{ background:'#2D5A4F' }}>{sending ? 'Sealing your letter...' : 'Seal & send to future me'}</button>
          </div>
        )}

        {tab === 'inbox' && (
          <div>
            {loading && <div style={{ textAlign:'center', padding:20 }}><Spinner /></div>}
            {!loading && letters.length === 0 && (
              <div className="card" style={{ textAlign:'center', padding:'32px 20px' }}>
                <div style={{ fontSize:32, marginBottom:12 }}>✉️</div>
                <div style={{ fontSize:14, fontWeight:600, color:'#333', marginBottom:6 }}>No letters yet</div>
                <div style={{ fontSize:12, color:'#888' }}>Write yourself a letter — your future self will thank you.</div>
              </div>
            )}
            {letters.map(l => (
              <div key={l.id} className="card" style={{ marginBottom:12, opacity: isReady(l) ? 1 : 0.7 }} onClick={() => isReady(l) && setOpenLetter(openLetter===l.id ? null : l.id)}>
                <div style={{ display:'flex', alignItems:'center', gap:10 }}>
                  <div style={{ fontSize:24 }}>{isReady(l) ? '✉️' : '🔒'}</div>
                  <div style={{ flex:1 }}>
                    <div style={{ fontSize:13, fontWeight:600, color:'#333' }}>{isReady(l) ? 'A letter from your past self' : 'Sealed letter'}</div>
                    <div style={{ fontSize:11, color:'#888', marginTop:2 }}>
                      {isReady(l) ? `Written ${new Date(l.created_at).toLocaleDateString('en-AU', { day:'numeric', month:'long' })}` : `Opens ${new Date(l.deliver_at).toLocaleDateString('en-AU', { day:'numeric', month:'long' })}`}
                    </div>
                  </div>
                  {isReady(l) && <div style={{ fontSize:12, color:'#2D5A4F' }}>{openLetter===l.id ? '▲' : '▼'}</div>}
                </div>
                {isReady(l) && openLetter===l.id && (
                  <div style={{ marginTop:16, paddingTop:16, borderTop:'1px solid #eee', fontFamily:"'Playfair Display',serif", fontSize:14, fontStyle:'italic', lineHeight:1.8, color:'#333' }}>
                    {l.content}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
      <Nav active="home" go={go} />
    </div>
  );
}
"""

# Add screen route
c = c.replace(
    '{screen === "sleep"      && <SleepScreen go={go} />}',
    '{screen === "sleep"      && <SleepScreen go={go} />}\n        {screen === "letters"    && <LetterScreen go={go} user={u} />}'
)

# Add card to home screen before sleep stories
c = c.replace(
    '{ ic:"🌙", t:"Sleep stories", s:"Drift off with a calming story", col:"#EEF2FF", sc:"sleep" },',
    '{ ic:"✉️", t:"Letters to yourself", s:"Write to your future self", col:"#f0f7f0", sc:"letters" },\n          { ic:"🌙", t:"Sleep stories", s:"Drift off with a calming story", col:"#EEF2FF", sc:"sleep" },'
)

# Add component before export default
c = c.replace('export default function App()', letter + '\nexport default function App()')

open('src/App.js', 'w').write(c)
print('done, lines:', len(c.splitlines()))
print('LetterScreen count:', c.count('function LetterScreen('))
