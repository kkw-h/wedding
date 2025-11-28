<template>
  <a-card :title="`项目详情：${id}`">
    <a-tabs v-model:activeKey="tab">
      <a-tab-pane key="overview" tab="概览">
        <div v-if="detail">新人：{{ detail.base_info?.groom }} & {{ detail.base_info?.bride }}</div>
      </a-tab-pane>
      <a-tab-pane key="budget" tab="预算">
        <BudgetTab :projectId="id" :role="userRole" />
      </a-tab-pane>
    </a-tabs>
  </a-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getProjectDetail } from '../../api/modules/projects'
import BudgetTab from './BudgetTab.vue'
import { useAuthStore } from '../../stores/auth'

const route = useRoute()
const id = route.params.id as string
const detail = ref<any>(null)
const auth = useAuthStore()
const userRole = auth.user?.role as any

onMounted(async () => { detail.value = await getProjectDetail(id) })
</script>

