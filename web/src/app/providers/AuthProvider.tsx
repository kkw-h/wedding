import { PropsWithChildren, createContext, useContext, useEffect, useState } from 'react'
import { supabase } from '@/shared/api/supabase'

type AuthContextType = {
  user: { id: string; email?: string } | null
  loading: boolean
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextType>({ user: null, loading: true, signOut: async () => {} })

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<{ id: string; email?: string } | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function init() {
      if (!supabase) { setLoading(false); return }
      const { data } = await supabase.auth.getUser()
      setUser(data.user ? { id: data.user.id, email: data.user.email || undefined } : null)
      setLoading(false)
    }
    init()
    const { data: sub } = supabase?.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ? { id: session.user.id, email: session.user.email || undefined } : null)
    }) || { data: { subscription: { unsubscribe() {} } } }
    return () => { sub.subscription?.unsubscribe?.() }
  }, [])

  async function signOut() {
    if (!supabase) return
    await supabase.auth.signOut()
  }

  return <AuthContext.Provider value={{ user, loading, signOut }}>{children}</AuthContext.Provider>
}

export function useAuth() { return useContext(AuthContext) }