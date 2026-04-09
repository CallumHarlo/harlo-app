c = open('src/App.js').read()

# Add Go Premium button to home screen near the bottom of the cards list
old = '{ ic:"🌙", t:"Sleep stories", s:"Drift off with a calming story", col:"#EEF2FF", sc:"sleep" },'
new = '{ ic:"✦", t:"Go Premium", s:"Unlock sleep stories, insights & more", col:"#2D5A4F", sc:"premium" },\n          { ic:"🌙", t:"Sleep stories", s:"Drift off with a calming story", col:"#EEF2FF", sc:"sleep" },'
c = c.replace(old, new)

open('src/App.js', 'w').write(c)
print('done')
