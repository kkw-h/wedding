import { supabase } from '@/shared/api/supabase'
import { Preplan } from '@/shared/api/types'

export async function listPreplans(keyword?: string): Promise<Preplan[]> {
  if (!supabase) return []
  let query = supabase.from('preplans').select('*').order('updated_at', { ascending: false })
  if (keyword && keyword.trim()) {
    query = query.or(`name.ilike.%${keyword}%,type.ilike.%${keyword}%`)
  }
  const { data } = await query
  return (data || []) as Preplan[]
}

export async function getPreplan(id: string): Promise<Preplan | null> {
  if (!supabase) return null
  const { data } = await supabase.from('preplans').select('*').eq('id', id).maybeSingle()
  return (data as Preplan) || null
}

export async function createPreplan(payload: { name: string; type: string; content_md: string; created_by: string; attachments?: string[] }): Promise<Preplan | null> {
  if (!supabase) return null
  const { data, error } = await supabase
    .from('preplans')
    .insert({ name: payload.name, type: payload.type || '未设定', content_md: payload.content_md, created_by: payload.created_by, attachments: payload.attachments || [] })
    .select('*')
    .maybeSingle()
  if (error) return null
  const created = data as Preplan
  await supabase.from('history').insert({ entity_type: 'preplans', entity_id: created.id, user_name: payload.created_by, action: 'create', details: `创建预案：${payload.name}` })
  return created
}

export async function updatePreplan(id: string, payload: { name: string; type: string; content_md: string }, user_name: string): Promise<Preplan | null> {
  if (!supabase) return null
  const { data, error } = await supabase
    .from('preplans')
    .update({ name: payload.name, type: payload.type || '未设定', content_md: payload.content_md })
    .eq('id', id)
    .select('*')
    .maybeSingle()
  if (error) return null
  const updated = data as Preplan
  await supabase.from('history').insert({ entity_type: 'preplans', entity_id: id, user_name, action: 'update', details: `更新预案：${payload.name}` })
  return updated
}

export async function logPreplanHistory(id: string, user_name: string, details: string) {
  if (!supabase) return
  await supabase.from('history').insert({ entity_type: 'preplans', entity_id: id, user_name, action: 'update', details })
}

export async function logPreplanHistoryBatch(id: string, user_name: string, ops: Array<{ type: string; field?: string; value?: any }>) {
  if (!supabase || !ops?.length) return
  const rows = ops.map((op) => ({
    entity_type: 'preplans',
    entity_id: id,
    user_name,
    action: 'update',
    details: op.field ? `${op.type}:${op.field}=${JSON.stringify(op.value)}` : op.type
  }))
  await supabase.from('history').insert(rows)
}