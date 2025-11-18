import { Button, Input, Space, Table, Tag } from 'antd'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listPreplans } from '../services/api'

function PreplanList() {
  const [keyword, setKeyword] = useState('')
  const [data, setData] = useState<any[]>([])

  useEffect(() => {
    listPreplans(keyword).then(setData)
  }, [keyword])
  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Space>
        <Input placeholder="搜索预案名称或类型" value={keyword} onChange={(e) => setKeyword(e.target.value)} />
        <Link to="/preplans/new"><Button type="primary">新建预案</Button></Link>
      </Space>
      <Table rowKey="id" dataSource={data} columns={[
        { title: '预案名称', dataIndex: 'name', render: (v: string, r: any) => <Link to={`/preplans/${r.id}`}>{v}</Link> },
        { title: '类型', dataIndex: 'type', render: (v: string) => <Tag>{v}</Tag> },
        { title: '创建人', dataIndex: 'createdBy' },
        { title: '最后更新时间', dataIndex: 'updatedAt' },
        { title: '操作', render: (_: any, r: any) => (
          <Space>
            <Link to={`/preplans/${r.id}`}>查看</Link>
            <Link to={`/preplans/${r.id}/edit`}>编辑</Link>
          </Space>
        ) }
      ]} />
    </Space>
  )
}

export default PreplanList