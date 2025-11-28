<template>
  <a-card title="方案列表">
    <template #extra>
      <a-button type="primary" @click="openCreate">新建方案</a-button>
    </template>
    
    <a-table :dataSource="list" :columns="columns" rowKey="id" :pagination="false">
      <template #bodyCell="{ column, record }">
        <template v-if="column.dataIndex === 'status'">
          {{ statusMap[record.status] || record.status }}
        </template>
        <template v-if="column.key === 'action'">
          <a-button type="link" @click="$router.push(`/proposals/${record.id}`)">编辑</a-button>
        </template>
      </template>
    </a-table>

    <a-modal v-model:open="createOpen" title="新建方案" @ok="create">
      <a-form layout="vertical">
        <a-form-item label="方案名称" required><a-input v-model:value="form.name" /></a-form-item>
        <a-form-item label="描述"><a-textarea v-model:value="form.description" /></a-form-item>
      </a-form>
    </a-modal>
  </a-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getProposalsByProject, createProposal, ProposalItem } from '../../api/modules/proposals'
import { message } from 'ant-design-vue'

const route = useRoute()
const projectId = route.params.id as string
const list = ref<ProposalItem[]>([])

const columns = [
  { title: '方案名称', dataIndex: 'name' },
  { title: '状态', dataIndex: 'status' },
  { title: '创建时间', dataIndex: 'created_at' },
  { title: '操作', key: 'action' }
]

const statusMap: Record<string, string> = {
  'DRAFT': '草稿',
  'ACTIVE': '进行中',
  'SELECTED': '已定稿',
  'ARCHIVED': '已归档'
}

async function load() {
  try {
    const resp = await getProposalsByProject(projectId)
    list.value = resp as any
  } catch (e: any) {
    message.error(e.message || '加载失败')
  }
}

const createOpen = ref(false)
const form = ref({ name: '', description: '' })

function openCreate() {
  form.value = { name: '', description: '' }
  createOpen.value = true
}

async function create() {
  if (!form.value.name) {
    message.error('请输入方案名称')
    return
  }
  try {
    await createProposal(projectId, form.value)
    message.success('创建成功')
    createOpen.value = false
    load()
  } catch (e: any) {
    message.error(e.message || '创建失败')
  }
}

onMounted(load)
</script>
