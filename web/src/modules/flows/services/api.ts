import { supabase } from '@/shared/api/supabase'
import { WeddingFlow } from '@/shared/api/types'

export async function listFlows(): Promise<WeddingFlow[]> {
  if (!supabase) return []
  const { data } = await supabase.from('wedding_flows').select('*').order('time', { ascending: true })
  return (data || []) as WeddingFlow[]
}