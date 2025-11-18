import { Button, Form, Input, InputNumber, Space } from 'antd'
import { useNavigate } from 'react-router-dom'

function VenueEdit() {
  const nav = useNavigate()
  return (
    <Form layout="vertical" onFinish={() => nav('/venues')}>
      <Form.Item label="场地名称" name="name" rules={[{ required: true }]}> 
        <Input />
      </Form.Item>
      <Form.Item label="类型" name="type"> 
        <Input />
      </Form.Item>
      <Form.Item label="位置" name="location"> 
        <Input />
      </Form.Item>
      <Form.Item label="价格" name="price"> 
        <InputNumber style={{ width: 200 }} />
      </Form.Item>
      <Form.Item label="描述" name="desc_md"> 
        <Input.TextArea rows={8} />
      </Form.Item>
      <Space>
        <Button type="primary" htmlType="submit">保存</Button>
        <Button onClick={() => nav('/venues')}>取消</Button>
      </Space>
    </Form>
  )
}

export default VenueEdit