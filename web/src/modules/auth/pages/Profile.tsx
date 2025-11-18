import { Button, Descriptions, Form, Input, Space, message } from 'antd'
import { useEffect, useState } from 'react'
import { useAuth } from '@/app/providers/AuthProvider'
import { supabase } from '@/shared/api/supabase'

function Profile() {
  const { user } = useAuth()
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    async function fetch() {
      if (!user || !supabase) return
      const { data } = await supabase.from('staff').select('*').eq('user_id', user.id).maybeSingle()
      if (data) form.setFieldsValue({ name: data.name, role: data.role, phone: data.phone || '', wechat: data.wechat || '' })
    }
    fetch()
  }, [user])

  async function onSave(values: any) {
    if (!user || !supabase) return
    setLoading(true)
    const { data: exists } = await supabase.from('staff').select('id').eq('user_id', user.id).maybeSingle()
    if (exists?.id) {
      await supabase.from('staff').update({ name: values.name, role: values.role, phone: values.phone, wechat: values.wechat }).eq('user_id', user.id)
    } else {
      await supabase.from('staff').insert({ user_id: user.id, name: values.name, role: values.role, phone: values.phone, wechat: values.wechat })
    }
    setLoading(false)
    message.success('已保存')
  }

  return (
    <Space direction="vertical" style={{ width: 480 }}>
      <Descriptions title="账户信息" column={1} items={[
        { key: 'email', label: '邮箱', children: user?.email }
      ]} />
      <Form layout="vertical" form={form} onFinish={onSave}>
        <Form.Item label="姓名" name="name" rules={[{ required: true }]}> <Input /> </Form.Item>
        <Form.Item label="角色类型" name="role" rules={[{ required: true }]}> <Input /> </Form.Item>
        <Form.Item label="电话" name="phone"> <Input /> </Form.Item>
        <Form.Item label="微信" name="wechat"> <Input /> </Form.Item>
        <Button type="primary" htmlType="submit" loading={loading}>保存</Button>
      </Form>
    </Space>
  )
}

export default Profile