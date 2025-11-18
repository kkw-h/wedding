import { Descriptions } from 'antd'
import { useParams } from 'react-router-dom'

function StaffDetail() {
  const { id } = useParams()
  const data = { id, name: '张三', role: '造型师', phone: '13812345678', wechat: 'wxid' }
  return (
    <Descriptions column={1} items={[
      { key: 'name', label: '姓名', children: data.name },
      { key: 'role', label: '角色', children: data.role },
      { key: 'phone', label: '电话', children: <a href={`tel:${data.phone}`}>{data.phone}</a> },
      { key: 'wechat', label: '微信', children: data.wechat }
    ]} />
  )
}

export default StaffDetail