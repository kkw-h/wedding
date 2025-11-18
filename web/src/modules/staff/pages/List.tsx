import { Table } from 'antd'
import { Link } from 'react-router-dom'
import { maskPhone } from '@/shared/utils/phone'
import { useEffect, useState } from 'react'
import { listStaff } from '../services/api'
import { useAuth } from '@/app/providers/AuthProvider'

function StaffList() {
  const [data, setData] = useState<any[]>([])
  const { user } = useAuth()
  useEffect(() => { listStaff().then(setData) }, [])
  return (
    <Table rowKey="id" dataSource={data} columns={[
      { title: '姓名', dataIndex: 'name', render: (v: string, r: any) => <Link to={`/staff/${r.id}`}>{v}</Link> },
      { title: '角色类型', dataIndex: 'role' },
      { title: '电话', dataIndex: 'phone', render: (v: string) => <a href={`tel:${v}`}>{maskPhone(v)}</a> },
      { title: '微信', dataIndex: 'wechat' },
      { title: '操作', render: (_: any, r: any) => (r.user_id && user?.id === r.user_id ? <Link to={`/staff/${r.id}/edit`}>编辑</Link> : null) }
    ]} />
  )
}

export default StaffList