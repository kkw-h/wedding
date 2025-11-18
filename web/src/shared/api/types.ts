export interface HistoryItem {
  user: string
  action: 'create' | 'update' | 'delete'
  timestamp: string
  details?: string
}

export interface Preplan {
  id: string
  name: string
  type: string
  content_md: string
  attachments: string[]
  history: HistoryItem[]
  createdBy: string
  updatedAt: string
}

export interface WeddingFlow {
  id: string
  step_name: string
  time: string
  owner_id: string
  owner_name: string
  phone: string
  note_md?: string
  history: HistoryItem[]
}

export interface Venue {
  id: string
  name: string
  type?: string
  location?: string
  price?: number
  desc_md?: string
  attachments?: string[]
  history: HistoryItem[]
}

export interface Staff {
  id: string
  name: string
  role: string
  phone?: string
  wechat?: string
  history: HistoryItem[]
}

export type BudgetCategory =
  | '场地'
  | '餐饮'
  | '婚纱照'
  | '花艺'
  | '摄影'
  | '化妆'
  | '交通'
  | '其他'

export interface BudgetItem {
  id: string
  name: string
  category: BudgetCategory
  amount: number
  note_md?: string
  attachments?: string[]
}