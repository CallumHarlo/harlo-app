import re

path = '/Users/callumbenson/Downloads/betteryou/src/App.js'

with open(path, 'r') as f:
    content = f.read()

# ── 1. REPLACE VAPID PLACEHOLDER ──────────────────────────────────────────
old_vapid = 'const VAPID_PUBLIC = "VAPID_PUBLIC_KEY_PLACEHOLDER";'
new_vapid = 'const VAPID_PUBLIC = "BLx4pccvNcrp9Pn1JtLXMXt0amqE4CqRJeVX1blVzi9HYeG-oFW_qUNotXN-kdfXnZ-TBRxOc7sAqVrwBM0hWl4";'

if old_vapid in content:
    content = content.replace(old_vapid, new_vapid)
    print("✓ VAPID public key updated")
else:
    print("✗ VAPID placeholder not found")

# ── 2. ADD HAPTIC FEEDBACK TO MOOD LOGGER ─────────────────────────────────
old_log = '''  const logMood = async (mood) => {
    if (savingMood) return;
    setSavingMood(true);'''

new_log = '''  const logMood = async (mood) => {
    if (savingMood) return;
    if (navigator.vibrate) navigator.vibrate(10);
    setSavingMood(true);'''

if old_log in content:
    content = content.replace(old_log, new_log)
    print("✓ Haptic feedback added to mood tap")
else:
    print("✗ Could not find logMood function")

with open(path, 'w') as f:
    f.write(content)

print("\nDone!")
