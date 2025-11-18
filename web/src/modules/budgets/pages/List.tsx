import { Input, Select, Space, Table } from 'antd'
import { useEffect, useState } from 'react'
import { listBudgets } from '../services/api'

function BudgetList() {
  const [category, setCategory] = useState<string | undefined>(undefined)
  const [keyword, setKeyword] = useState('')
  const [data, setData] = useState<any[]>([])
  useEffect(() => { listBudgets(category, keyword).then(setData) }, [category, keyword])
  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Space>
        <Select placeholder="分类筛选" style={{ width: 160 }} value={category} onChange={setCategory} allowClear options={[
          { value: '场地', label: '场地' },
          { value: '餐饮', label: '餐饮' },
          { value: '婚纱照', label: '婚纱照' },
          { value: '花艺', label: '花艺' },
          { value: '摄影', label: '摄影' },
          { value: '化妆', label: '化妆' },
          { value: '交通', label: '交通' },
          { value: '其他', label: '其他' }
        ]} />
        <Input placeholder="搜索预算项名称" style={{ width: 240 }} value={keyword} onChange={(e) => setKeyword(e.target.value)} />
      </Space>
      <Table rowKey="id" dataSource={data} columns={[
        { title: '预算项名称', dataIndex: 'name' },
        { title: '分类', dataIndex: 'category' },
        { title: '金额', dataIndex: 'amount' },
        { title: '备注', dataIndex: 'note_md' }
      ]} />
    </Space>
  )
}

export default BudgetList