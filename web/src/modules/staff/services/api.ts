import { supabase } from '@/shared/api/supabase'
import { Staff } from '@/shared/api/types'

export async function listStaff(): Promise<Staff[]> {
  if (!supabase) return []
  const { data } = await supabase.from('staff').select('*').order('name', { ascending: true })
  return (data || []) as Staff[]
}