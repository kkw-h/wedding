import { supabase } from '@/shared/api/supabase'

export async function signIn(email: string, password: string) {
  if (!supabase) throw new Error('Supabase 未配置')
  const { error } = await supabase.auth.signInWithPassword({ email, password })
  if (error) throw error
}

export async function signUp(email: string, password: string) {
  if (!supabase) throw new Error('Supabase 未配置')
    console.log(supabase)
  const { error } = await supabase.auth.signUp({ email, password, options: {
    "emailRedirectTo": "http://localhost:3000/auth/callback"
  } })
  console.log(error?.message)
  if (error) throw error
}