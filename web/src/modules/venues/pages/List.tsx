import { Table } from 'antd'
import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { listVenues } from '../services/api'

function VenueList() {
  const [data, setData] = useState<any[]>([])
  useEffect(() => { listVenues().then(setData) }, [])
  return (
    <Table rowKey="id" dataSource={data} columns={[
      { title: '场地名称', dataIndex: 'name', render: (v: string, r: any) => <Link to={`/venues/${r.id}`}>{v}</Link> },
      { title: '类型', dataIndex: 'type' },
      { title: '位置', dataIndex: 'location' },
      { title: '价格', dataIndex: 'price' },
      { title: '操作', render: (_: any, r: any) => <Link to={`/venues/${r.id}/edit`}>编辑</Link> }
    ]} />
  )
}

export default VenueList