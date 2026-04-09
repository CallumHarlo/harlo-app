import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import webpush from "npm:web-push@3.6.7";

const VAPID_PUBLIC = Deno.env.get("VAPID_PUBLIC_KEY") || "";
const VAPID_PRIVATE = Deno.env.get("VAPID_PRIVATE_KEY") || "";

serve(async () => {
  try {
    webpush.setVapidDetails("mailto:admin@betteryou.app", VAPID_PUBLIC, VAPID_PRIVATE);

    const supabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
    );

    const now = new Date();
    const perthHours = (now.getUTCHours() + 8) % 24;
    const currentTime = String(perthHours).padStart(2, "0") + ":" + String(now.getUTCMinutes()).padStart(2, "0");
    console.log("Perth time:", currentTime);

    const { data: reminders } = await supabase
      .from("reminders")
      .select("user_id, journal_time, journal_on")
      .eq("journal_on", true)
      .eq("journal_time", currentTime);

    console.log("Matches:", reminders?.length || 0);

    const messages = [
      "How are you feeling today? Take 5 minutes to write it out.",
      "Your journal is waiting. Even a few words can make a difference.",
      "Check in with yourself today. What's on your mind?",
      "A moment of reflection can change your whole day.",
    ];

    for (const rem of (reminders || [])) {
      const { data: sub } = await supabase
        .from("push_subscriptions")
        .select("subscription")
        .eq("user_id", rem.user_id)
        .single();

      if (!sub?.subscription?.endpoint) { console.log("No sub for:", rem.user_id); continue; }

      const msg = messages[Math.floor(Math.random() * messages.length)];
      const payload = JSON.stringify({ title: "Better You ✍️", body: msg });

      try {
        const result = await webpush.sendNotification(sub.subscription, payload);
        console.log("Push sent:", result.statusCode);
      } catch (pushErr) {
        console.log("Push error:", String(pushErr));
      }
    }

    return new Response("Done. Perth: " + currentTime + " Matches: " + (reminders?.length || 0), { status: 200 });
  } catch (e) {
    console.error("Error:", String(e));
    return new Response("Error: " + String(e), { status: 500 });
  }
});
