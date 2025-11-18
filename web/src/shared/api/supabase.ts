import { createClient } from '@supabase/supabase-js'

function clean(v: unknown) {
  return String(v || '').trim().replace(/^['"]|['"]$/g, '')
}

const rawUrl = (import.meta as any).env.VITE_SUPABASE_URL
const rawAnon = (import.meta as any).env.VITE_SUPABASE_ANON_KEY
const url = clean(rawUrl)
const anon = clean(rawAnon)

export const supabase = url && anon ? createClient(url, anon) : undefined