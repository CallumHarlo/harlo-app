import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const ANTHROPIC_KEY = Deno.env.get("ANTHROPIC_API_KEY") || "";
const SUPABASE_URL = Deno.env.get("SUPABASE_URL") || "";
const SUPABASE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "";

serve(async () => {
  try {
    const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
    console.log("Starting quote generation");

    const { data: subs, error: subErr } = await supabase
      .from("push_subscriptions")
      .select("user_id");

    console.log("Subs:", JSON.stringify(subs), "Error:", JSON.stringify(subErr));

    if (!subs?.length) {
      console.log("No subscribers");
      return new Response("No subscribers", { status: 200 });
    }

    for (const { user_id } of subs) {
      console.log("Processing user:", user_id);

      const { data: entries } = await supabase
        .from("entries")
        .select("tags")
        .eq("user_id", user_id)
        .order("created_at", { ascending: false })
        .limit(5);

      const moodSummary = entries?.flatMap((e: any) => e.tags || []).join(", ") || "general wellbeing";
      console.log("Moods:", moodSummary);

      const r = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": ANTHROPIC_KEY,
          "anthropic-version": "2023-06-01"
        },
        body: JSON.stringify({
          model: "claude-haiku-4-5-20251001",
          max_tokens: 80,
          messages: [{
            role: "user",
            content: `Write a short motivational quote (1 sentence, max 20 words) for someone whose recent moods include: ${moodSummary}. Be warm and uplifting. No attribution.`
          }]
        })
      });

      const data = await r.json();
      const quote = data.content?.[0]?.text || "You are doing better than you think.";
      console.log("Quote:", quote);

      const { error: updateErr } = await supabase
        .from("profiles")
        .update({ daily_quote: quote, quote_date: new Date().toISOString().split("T")[0] })
        .eq("id", user_id);

      console.log("Update error:", JSON.stringify(updateErr));
    }

    return new Response("Done", { status: 200 });
  } catch (e) {
    console.error("Error:", e);
    return new Response("Error: " + e.message, { status: 500 });
  }
});
