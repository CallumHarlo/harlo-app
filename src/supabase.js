import { createClient } from '@supabase/supabase-js';
const SUPABASE_URL = 'https://ptfqfdimzokpifrdxggs.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB0ZnFmZGltem9rcGlmcmR4Z2dzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ0MjMwODEsImV4cCI6MjA4OTk5OTA4MX0.TReru209WRcsP-LS5ngabY9awcidLwrXWd1vohK4dTo';
export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
