# Better You — Mental Wellness App

## Setup

1. Install dependencies:
```
npm install
```

2. **Add your Anthropic API key:**
   Open `src/App.js` and find line 6:
   ```js
   const ANTHROPIC_API_KEY = "YOUR_API_KEY_HERE";
   ```
   Replace `YOUR_API_KEY_HERE` with your actual key from console.anthropic.com

3. Run the app:
```
npm start
```
Opens at http://localhost:3000

## Turn into a mobile app (optional)
```
npm install -g @capacitor/cli
npx cap init
npm run build
npx cap add ios
npx cap add android
npx cap open ios     # Opens in Xcode
npx cap open android # Opens in Android Studio
```

## Features
- Login screen
- Home with Cheers strip
- New journal entry with mood tags (incl. sad)
- AI reflection (powered by Claude)
- Self-response to past entries
- Publish & share screen
- Cheers inbox (prompts, photos, voice notes)
- Send a cheer to friends
- Reminders & notifications settings

## Security
- Never commit your API key to GitHub
- Add `src/App.js` to `.gitignore` or use a `.env` file
