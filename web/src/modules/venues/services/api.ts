import { supabase } from '@/shared/api/supabase'
import { Venue } from '@/shared/api/types'

export async function listVenues(): Promise<Venue[]> {
  if (!supabase) return []
  const { data } = await supabase.from('venues').select('*').order('updated_at', { ascending: false })
  return (data || []) as Venue[]
}