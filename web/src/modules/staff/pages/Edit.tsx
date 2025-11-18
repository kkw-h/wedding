import { Button, Form, Input, Space } from 'antd'
import { useNavigate } from 'react-router-dom'

function StaffEdit() {
  const nav = useNavigate()
  return (
    <Form layout="vertical" onFinish={() => nav('/staff')}>
      <Form.Item label="姓名" name="name" rules={[{ required: true }]}> 
        <Input />
      </Form.Item>
      <Form.Item label="角色类型" name="role"> 
        <Input />
      </Form.Item>
      <Form.Item label="电话" name="phone"> 
        <Input />
      </Form.Item>
      <Form.Item label="微信" name="wechat"> 
        <Input />
      </Form.Item>
      <Space>
        <Button type="primary" htmlType="submit">保存</Button>
        <Button onClick={() => nav('/staff')}>取消</Button>
      </Space>
    </Form>
  )
}

export default StaffEdit