c = open('src/App.js').read()

# Add isPremium state
c = c.replace(
    '  const [isReset, setIsReset] = useState(false);',
    '  const [isReset, setIsReset] = useState(false);\n  const [isPremium, setIsPremium] = useState(false);'
)

# Load isPremium from profile
c = c.replace(
    'select("has_onboarded")',
    'select("has_onboarded,is_premium")'
)
c = c.replace(
    'if (!data?.has_onboarded) setNeedsOnboarding(true); });',
    'if (!data?.has_onboarded) setNeedsOnboarding(true); if (data?.is_premium) setIsPremium(true); });'
)

# Add premium screen route
c = c.replace(
    '{screen === "sleep"      && <SleepScreen go={go} />}',
    '{screen === "sleep"      && <SleepScreen go={go} isPremium={isPremium} />}\n        {screen === "premium"    && <PremiumScreen go={go} user={u} onUpgrade={() => setIsPremium(true)} />}'
)

# Pass isPremium to HomeScreen
c = c.replace(
    '<HomeScreen go={go} user={u} cheers={cheers} />',
    '<HomeScreen go={go} user={u} cheers={cheers} isPremium={isPremium} />'
)

open('src/App.js', 'w').write(c)
print('done')
