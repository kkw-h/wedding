import { Form, Input, TimePicker, Button, Space } from 'antd'
import dayjs from 'dayjs'
import { useNavigate } from 'react-router-dom'

function FlowEdit() {
  const nav = useNavigate()
  return (
    <Form layout="vertical" onFinish={() => nav('/flows')}>
      <Form.Item label="步骤名称" name="step_name" rules={[{ required: true }]}> 
        <Input />
      </Form.Item>
      <Form.Item label="时间" name="time" rules={[{ required: true }]}> 
        <TimePicker format="HH:mm" defaultOpenValue={dayjs('00:00', 'HH:mm')} />
      </Form.Item>
      <Form.Item label="负责人" name="owner_name"> 
        <Input />
      </Form.Item>
      <Form.Item label="电话" name="phone"> 
        <Input disabled />
      </Form.Item>
      <Form.Item label="备注" name="note_md"> 
        <Input.TextArea rows={6} />
      </Form.Item>
      <Space>
        <Button type="primary" htmlType="submit">保存</Button>
        <Button onClick={() => nav('/flows')}>取消</Button>
      </Space>
    </Form>
  )
}

export default FlowEdit