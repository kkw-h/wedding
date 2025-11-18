import { supabase } from '@/shared/api/supabase'
import { BudgetItem } from '@/shared/api/types'

export async function listBudgets(category?: string, keyword?: string): Promise<BudgetItem[]> {
  if (!supabase) return []
  let query = supabase.from('budgets').select('*')
  if (category) query = query.eq('category', category)
  if (keyword && keyword.trim()) query = query.ilike('name', `%${keyword}%`)
  const { data } = await query
  return (data || []) as BudgetItem[]
}