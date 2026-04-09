c = open('src/App.js').read()

eula = """
function EulaScreen({ onAccept }) {
  return (
    <div className="screen" style={{ background:'#2D5A4F' }}>
      <div style={{ padding:'52px 20px 32px', flex:1, overflowY:'auto' }}>
        <div style={{ fontFamily:"'Playfair Display',serif", fontSize:28, color:'white', fontWeight:600, marginBottom:8 }}>Welcome to Harlo</div>
        <div style={{ fontSize:13, color:'rgba(255,255,255,.65)', marginBottom:28, lineHeight:1.6 }}>Before you join our community, please read and agree to our terms.</div>
        <div style={{ background:'rgba(255,255,255,.1)', borderRadius:16, padding:20, marginBottom:20 }}>
          <div style={{ fontSize:13, fontWeight:600, color:'white', marginBottom:10 }}>Community Guidelines</div>
          <div style={{ fontSize:12, color:'rgba(255,255,255,.7)', lineHeight:1.8 }}>
            By using Harlo you agree to:<br/><br/>
            ✦ Treat all members with kindness and respect<br/>
            ✦ Not post harmful, abusive or offensive content<br/>
            ✦ Not harass, bully or threaten other users<br/>
            ✦ Report content that violates these guidelines<br/>
            ✦ We have zero tolerance for objectionable content<br/><br/>
            We review all reports within 24 hours and will remove content and users who violate these terms.
          </div>
        </div>
        <div style={{ background:'rgba(255,255,255,.1)', borderRadius:16, padding:20, marginBottom:28 }}>
          <div style={{ fontSize:13, fontWeight:600, color:'white', marginBottom:10 }}>Privacy & Data</div>
          <div style={{ fontSize:12, color:'rgba(255,255,255,.7)', lineHeight:1.8 }}>
            Your journal entries are private and only visible to you. Community posts are visible to other Harlo members. We never sell your personal data. For support visit harlo-app.vercel.app/support.html
          </div>
        </div>
        <button onClick={onAccept} className="pbtn" style={{ background:'white', color:'#2D5A4F', fontSize:16, padding:'15px 0', fontWeight:700, marginBottom:12 }}>
          I agree — take me to Harlo
        </button>
        <div style={{ textAlign:'center', fontSize:11, color:'rgba(255,255,255,.4)' }}>By tapping above you agree to our Terms of Use and Community Guidelines</div>
      </div>
    </div>
  );
}
"""

# Add EULA check in App component - show EULA before community/publish features
# Add eulaAccepted state
c = c.replace(
    '  const [isPremium, setIsPremium] = useState(false);',
    '  const [isPremium, setIsPremium] = useState(false);\n  const [eulaAccepted, setEulaAccepted] = useState(() => !!localStorage.getItem("harlo_eula"));'
)

# Add EULA screen to render - show when accessing community or publish
c = c.replace(
    '{screen === "community" && <CommunityScreen go={go} user={u} />}',
    '{screen === "community" && !eulaAccepted && <EulaScreen onAccept={() => { localStorage.setItem("harlo_eula","1"); setEulaAccepted(true); }} />}\n        {screen === "community" && eulaAccepted && <CommunityScreen go={go} user={u} />}'
)

# Add component before export default
c = c.replace('export default function App()', eula + '\nexport default function App()')

open('src/App.js', 'w').write(c)
print('done, lines:', len(c.splitlines()))
print('EulaScreen count:', c.count('function EulaScreen('))
