<template>
  <a-card title="线索列表">
    <a-space style="margin-bottom:12px">
      <a-input v-model:value="keyword" placeholder="搜索姓名/手机号" style="width:220px" />
      <a-select v-model:value="status" style="width:180px" :options="statusOptions" />
      <a-button type="primary" @click="load">查询</a-button>
      <a-button @click="openCreate">新建线索</a-button>
    </a-space>
    <a-table :dataSource="list" :columns="columns" rowKey="id" :pagination="{total, current: page, pageSize: size, onChange: onPage}" />
    <a-modal v-model:open="createOpen" title="新建线索" @ok="create">
      <a-form layout="vertical">
        <a-form-item label="姓名"><a-input v-model:value="form.customer_name" /></a-form-item>
        <a-form-item label="手机号"><a-input v-model:value="form.phone" /></a-form-item>
        <a-form-item label="来源"><a-input v-model:value="form.source" /></a-form-item>
      </a-form>
    </a-modal>
    <a-modal v-model:open="convertOpen" title="转为项目" @ok="doConvert">
      <a-form layout="vertical">
        <a-form-item label="项目名称" required><a-input v-model:value="convertForm.name" /></a-form-item>
        <a-form-item label="婚期" required><a-date-picker v-model:value="convertForm.wedding_date" value-format="YYYY-MM-DD" style="width: 100%" /></a-form-item>
        <a-form-item label="酒店"><a-input v-model:value="convertForm.hotel_name" /></a-form-item>
        <a-form-item label="总预算"><a-input-number v-model:value="convertForm.total_budget" style="width: 100%" /></a-form-item>
      </a-form>
    </a-modal>
  </a-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getLeads, createLead, claimLead, deleteLead, LeadItem } from '../../api/modules/leads'
import { createProject } from '../../api/modules/projects'
import { message, Popconfirm } from 'ant-design-vue'

const keyword = ref('')
const status = ref<string | undefined>(undefined)
const statusOptions = [
  { label: '全部', value: undefined },
  { label: 'NEW', value: 'NEW' },
  { label: 'CONTACTING', value: 'CONTACTING' },
  { label: 'PUBLIC_POOL', value: 'PUBLIC_POOL' }
]

const page = ref(1)
const size = ref(10)
const total = ref(0)
const list = ref<LeadItem[]>([])

import { h } from 'vue'
import { Space, Button } from 'ant-design-vue'
const columns = [
  { title: '姓名', dataIndex: 'customer_name' },
  { title: '手机号', dataIndex: 'phone' },
  { title: '婚期', dataIndex: 'wedding_date' },
  { title: '负责人', dataIndex: 'owner_name' },
  { 
    title: '操作', 
    key: 'actions', 
    customRender: ({ record }: any) => h(Space, {}, { 
      default: () => [
        h(Button, { size: 'small', onClick: () => onClaim(record.id) }, { default: () => '捞取' }),
        h(Button, { size: 'small', type: 'primary', onClick: () => onConvert(record) }, { default: () => '转为项目' }),
        h(Popconfirm, {
          title: '确定要删除此线索吗？',
          onConfirm: () => onDelete(record.id)
        }, {
          default: () => h(Button, { size: 'small', danger: true }, { default: () => '删除' })
        })
      ] 
    }) 
  }
]

async function load() {
  const resp = await getLeads({ page: page.value, size: size.value, status: status.value, keyword: keyword.value || undefined })
  total.value = resp.total
  list.value = resp.list
}

function onPage(p: number, s: number) { page.value = p; size.value = s; load() }

async function onClaim(id: string) { await claimLead(id); load() }

async function onDelete(id: string) {
  try {
    await deleteLead(id)
    message.success('删除成功')
    load()
  } catch (e: any) {
    message.error(e.message || '删除失败')
  }
}

const createOpen = ref(false)
const form = ref<{ customer_name: string; phone: string; source?: string }>({ customer_name: '', phone: '', source: '' })
function openCreate() { createOpen.value = true }
async function create() { await createLead(form.value); createOpen.value = false; load() }

const convertOpen = ref(false)
const convertForm = ref({ lead_id: '', name: '', wedding_date: '', hotel_name: '', total_budget: 0 })
function onConvert(record: any) {
  convertForm.value = {
    lead_id: record.id,
    name: `${record.customer_name}的婚礼`,
    wedding_date: record.wedding_date || '',
    hotel_name: '',
    total_budget: 0
  }
  convertOpen.value = true
}
async function doConvert() {
  if (!convertForm.value.name || !convertForm.value.wedding_date) {
    message.error('请填写完整信息')
    return
  }
  try {
    await createProject(convertForm.value)
    message.success('转化成功')
    convertOpen.value = false
    load()
  } catch(e: any) {
    message.error(e.message || '转化失败')
  }
}

onMounted(load)
</script>
