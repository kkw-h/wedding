import { Card, Space, Tag } from 'antd'
import { useParams, Link } from 'react-router-dom'
import MarkdownView from '@/shared/components/MarkdownView/MarkdownView'
import HistoryPanel from '@/shared/components/HistoryPanel/HistoryPanel'

function PreplanDetail() {
  const { id } = useParams()
  const data = { id, name: '示例预案', type: '类型', content_md: '# 详情', attachments: [], history: [], createdBy: '用户', updatedAt: new Date().toISOString() }
  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Space align="center">
        <h2 style={{ margin: 0 }}>{data.name}</h2>
        <Tag>{data.type}</Tag>
        <Link to={`/preplans/${id}/edit`}>编辑</Link>
      </Space>
      <Card>
        <MarkdownView content={data.content_md} />
      </Card>
      <HistoryPanel history={data.history} />
      <Link to="/preplans">返回列表</Link>
    </Space>
  )
}

export default PreplanDetail