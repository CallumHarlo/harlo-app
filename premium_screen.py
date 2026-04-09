c = open('src/App.js').read()

premium = '''
function PremiumScreen({ go, user, onUpgrade }) {
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  const activate = async () => {
    setLoading(true);
    await supabase.from('profiles').update({ is_premium: true, premium_since: new Date().toISOString() }).eq('id', user.id);
    setDone(true);
    setLoading(false);
    if (onUpgrade) onUpgrade();
    setTimeout(() => go('home'), 1500);
  };

  return (
    <div className="screen" style={{ background:'#2D5A4F' }}>
      <div style={{ padding:'52px 20px 20px' }}>
        <div style={{ fontSize:11, color:'rgba(255,255,255,.5)', cursor:'pointer', marginBottom:12 }} onClick={() => go('home')}>← back</div>
        <div style={{ fontFamily:"'Playfair Display',serif", fontSize:28, color:'white', fontWeight:600, marginBottom:6 }}>Harlo Premium</div>
        <div style={{ fontSize:13, color:'rgba(255,255,255,.65)', marginBottom:32 }}>Everything you need for every high and every low</div>
        <div style={{ background:'rgba(255,255,255,.1)', borderRadius:16, padding:20, marginBottom:16 }}>
          {[
            { e:'🌙', t:'Sleep Stories', s:'Calming ambient sounds to help you drift off' },
            { e:'💊', t:'Medication Tracking', s:'Never miss a dose with daily reminders' },
            { e:'📊', t:'Weekly Insights', s:'Deep dive into your mood patterns' },
            { e:'💬', t:'Unlimited AI Reflections', s:'Get thoughtful responses to every entry' },
            { e:'🖼', t:'Photo Cheers', s:'Send photos to friends and supporters' },
            { e:'✦', t:'Priority Support', s:'Get help when you need it most' },
          ].map((f,i) => (
            <div key={i} style={{ display:'flex', alignItems:'center', gap:12, marginBottom:i<5?16:0 }}>
              <div style={{ fontSize:22, width:32, textAlign:'center' }}>{f.e}</div>
              <div>
                <div style={{ fontSize:13, fontWeight:600, color:'white' }}>{f.t}</div>
                <div style={{ fontSize:11, color:'rgba(255,255,255,.55)', marginTop:1 }}>{f.s}</div>
              </div>
            </div>
          ))}
        </div>
        <div style={{ background:'rgba(255,255,255,.08)', borderRadius:16, padding:20, marginBottom:20, textAlign:'center' }}>
          <div style={{ fontSize:11, color:'rgba(255,255,255,.5)', marginBottom:4, textTransform:'uppercase', letterSpacing:'.1em' }}>Most popular</div>
          <div style={{ fontSize:32, fontWeight:700, color:'white' }}>$6.99<span style={{ fontSize:14, fontWeight:400 }}>/month</span></div>
          <div style={{ fontSize:12, color:'rgba(255,255,255,.5)', marginTop:4 }}>or $49.99/year — save 40%</div>
        </div>
        {done && <div className="ok" style={{ marginBottom:12 }}>Welcome to Premium! ✦</div>}
        <button className="pbtn" onClick={activate} disabled={loading || done} style={{ background:'white', color:'#2D5A4F', fontSize:16, padding:'15px 0', fontWeight:700 }}>
          {loading ? 'Activating...' : done ? 'Activated!' : 'Start 7-day free trial'}
        </button>
        <div style={{ textAlign:'center', fontSize:11, color:'rgba(255,255,255,.35)', marginTop:12 }}>Cancel anytime. No commitment.</div>
      </div>
    </div>
  );
}
'''

c = c.replace('export default function App()', premium + '\nexport default function App()')
open('src/App.js', 'w').write(c)
print('done, lines:', len(c.splitlines()))
