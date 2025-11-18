import { Card, Space, Tag } from 'antd'
import { useParams, Link } from 'react-router-dom'
import MarkdownView from '@/shared/components/MarkdownView/MarkdownView'
import HistoryPanel from '@/shared/components/HistoryPanel/HistoryPanel'
import { useEffect, useState } from 'react'
import { getPreplan, getPreplanHistory } from '../services/api'

function PreplanDetail() {
  const { id } = useParams()
  const [name, setName] = useState('')
  const [type, setType] = useState('')
  const [content, setContent] = useState('')
  const [history, setHistory] = useState<any[]>([])

  useEffect(() => {
    if (!id) return
    getPreplan(id).then((d) => {
      if (d) {
        setName(d.name)
        setType(d.type)
        setContent(d.content_md || '')
      }
    })
    getPreplanHistory(id).then(setHistory)
  }, [id])
  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Space align="center">
        <h2 style={{ margin: 0 }}>{name || '预案详情'}</h2>
        {type ? <Tag>{type}</Tag> : null}
        <Link to={`/preplans/${id}/edit`}>编辑</Link>
      </Space>
      <Card>
        <MarkdownView content={content} />
      </Card>
      <HistoryPanel history={history} />
      <Link to="/preplans">返回列表</Link>
    </Space>
  )
}

export default PreplanDetail