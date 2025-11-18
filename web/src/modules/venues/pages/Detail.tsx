import { Card, Space } from 'antd'
import { useParams } from 'react-router-dom'
import MarkdownView from '@/shared/components/MarkdownView/MarkdownView'

function VenueDetail() {
  const { id } = useParams()
  const data = { id, name: '场地', type: '类型', location: '位置', price: 5000, desc_md: '# 描述', attachments: [], history: [] }
  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <h2 style={{ margin: 0 }}>{data.name}</h2>
      <div>{data.type} | {data.location} | ¥{data.price}</div>
      <Card>
        <MarkdownView content={data.desc_md || ''} />
      </Card>
    </Space>
  )
}

export default VenueDetail