<template>
  <a-card title="项目列表">
    <a-space style="margin-bottom:12px">
      <a-button type="primary" @click="load">刷新</a-button>
    </a-space>
    <a-table :dataSource="list" :columns="columns" rowKey="id" :pagination="false" />
  </a-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getProjects, ProjectItem } from '../../api/modules/projects'
import { useRouter } from 'vue-router'
import { h } from 'vue'
import { Button, Space } from 'ant-design-vue'

const list = ref<ProjectItem[]>([])
const router = useRouter()

const columns = [
  { title: '项目名称', dataIndex: 'name' },
  { title: '婚期', dataIndex: 'wedding_date' },
  { title: '酒店', dataIndex: 'hotel_name' },
  { title: '总预算', dataIndex: 'total_budget' },
  { title: '阶段', dataIndex: 'stage' },
  {
    title: '操作',
    key: 'actions',
    customRender: ({ record }: any) => h(Space, {}, {
      default: () => [
        h(Button, {
          size: 'small',
          onClick: () => router.push(`/projects/${record.id}`)
        }, { default: () => '详情' }),
        h(Button, {
          size: 'small',
          onClick: () => router.push(`/projects/${record.id}/proposals`)
        }, { default: () => '查看预案' })
      ]
    })
  }
]

async function load() {
  const resp = await getProjects({ skip: 0, limit: 100 })
  list.value = resp as any
}

onMounted(load)
</script>

