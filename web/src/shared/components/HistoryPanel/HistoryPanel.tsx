import { Collapse, List } from 'antd'
import { HistoryItem } from '@/shared/api/types'

interface Props {
  history: HistoryItem[]
}

function HistoryPanel({ history }: Props) {
  return (
    <Collapse items={[{ key: 'history', label: '操作历史', children: (
      <List
        size="small"
        dataSource={[...history].sort((a, b) => (a.timestamp < b.timestamp ? 1 : -1))}
        renderItem={(h) => (
          <List.Item>
            [{new Date(h.timestamp).toLocaleString()}] {h.user} {h.action}：{h.details || ''}
          </List.Item>
        )}
      />
    ) }]} />
  )
}

export default HistoryPanel