import { Table } from 'antd'
import { useEffect, useState } from 'react'
import { listFlows } from '../services/api'

function FlowList() {
  const [data, setData] = useState<any[]>([])
  useEffect(() => { listFlows().then(setData) }, [])
  return (
    <Table rowKey="id" dataSource={data} columns={[
      { title: '时间', dataIndex: 'time' },
      { title: '步骤名称', dataIndex: 'step_name' },
      { title: '负责人', dataIndex: 'owner_name' },
      { title: '备注', dataIndex: 'note_md' }
    ]} />
  )
}

export default FlowList