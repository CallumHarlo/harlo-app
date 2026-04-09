const rateLimit = new Map();

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end();

  // Rate limiting: max 20 requests per IP per hour
  const ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress || 'unknown';
  const now = Date.now();
  const windowMs = 60 * 60 * 1000;
  const max = 20;
  if (!rateLimit.has(ip)) rateLimit.set(ip, []);
  const timestamps = rateLimit.get(ip).filter(t => now - t < windowMs);
  if (timestamps.length >= max) {
    return res.status(429).json({ reply: "You're reflecting a lot today — take a breath and come back soon." });
  }
  timestamps.push(now);
  rateLimit.set(ip, timestamps);

  // Block empty or very short inputs
  const { text } = req.body;
  if (!text || text.trim().length < 3) {
    return res.status(400).json({ reply: "Please write a little more before reflecting." });
  }

  // Truncate very long inputs to prevent abuse
  const truncated = text.slice(0, 1000);

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 200,
        system: 'You are Better You, a warm compassionate mental wellness companion. Respond to journal entries with a short empathetic reflection (2-3 sentences). Reflect what you hear with care, end with a gentle open question. Sound human and warm. Never use markdown formatting like asterisks or bold text.',
        messages: [{ role: 'user', content: `My journal entry: "${truncated}"` }]
      })
    });
    const data = await response.json();
    const reply = data.content?.[0]?.text || 'Thank you for sharing. Your feelings matter.';
    res.status(200).json({ reply });
  } catch(err) {
    res.status(200).json({ reply: 'Thank you for sharing that. Your feelings matter.' });
  }
}
