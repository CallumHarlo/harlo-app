
import sys
app_path = 'src/App.js'
c = open(app_path).read()
sleep = open('sleep_code.txt').read()
c = c.replace('export default function App()', sleep + chr(10) + 'export default function App()')
open(app_path,'w').write(c)
print('done - lines:', len(c.splitlines()))
print('count:', c.count('function SleepScreen('))
