import { Button, Form, Input, Space, message } from 'antd'
import { useEffect, useRef } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { createPreplan, getPreplan, updatePreplan, logPreplanHistoryBatch } from '../services/api'
import { useAuth } from '@/app/providers/AuthProvider'

function PreplanEdit() {
  const { id } = useParams()
  const nav = useNavigate()
  const [form] = Form.useForm()
  const { user } = useAuth()
  const opsRef = useRef<Array<{ type: string; field?: string; value?: any }>>([])

  useEffect(() => {
    if (id) {
      getPreplan(id).then((data) => {
        if (data) form.setFieldsValue({ name: data.name, type: data.type, content_md: data.content_md })
      })
      opsRef.current.push({ type: 'open_edit' })
    }
  }, [id])

  async function onSubmit(values: any) {
    if (!id) {
      const created = await createPreplan({ name: values.name, type: values.type, content_md: values.content_md, created_by: user?.email || '匿名' })
      if (created) {
        const u = user?.email || '匿名'
        const ops = [...opsRef.current, { type: 'submit_create' }]
        await logPreplanHistoryBatch(created.id, u, ops)
        message.success('创建成功')
        nav('/preplans')
      } else {
        message.error('创建失败')
      }
    } else {
      const updated = await updatePreplan(id, { name: values.name, type: values.type, content_md: values.content_md }, user?.email || '匿名')
      if (updated) {
        const u = user?.email || '匿名'
        const ops = [...opsRef.current, { type: 'submit_update' }]
        await logPreplanHistoryBatch(id, u, ops)
        message.success('更新成功')
        nav('/preplans')
      } else {
        message.error('更新失败')
      }
    }
  }
  return (
    <Form layout="vertical" form={form} onFinish={onSubmit} onValuesChange={(changed) => {
      const k = Object.keys(changed)[0]
      const v = (changed as any)[k]
      opsRef.current.push({ type: 'field_change', field: k, value: v })
    }}>
      <Form.Item label="预案名称" name="name" rules={[{ required: true }]}> 
        <Input />
      </Form.Item>
      <Form.Item label="预案类型" name="type" rules={[{ required: true, message: '请输入预案类型' }]}> 
        <Input />
      </Form.Item>
      <Form.Item label="描述内容" name="content_md"> 
        <Input.TextArea rows={8} />
      </Form.Item>
      <Space>
        <Button type="primary" htmlType="submit">保存</Button>
        <Button onClick={async () => {
          if (id) {
            const u = user?.email || '匿名'
            const ops = [...opsRef.current, { type: 'cancel' }]
            await logPreplanHistoryBatch(id, u, ops)
          }
          nav('/preplans')
        }}>取消</Button>
      </Space>
    </Form>
  )
}

export default PreplanEdit