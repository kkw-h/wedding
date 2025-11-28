<template>
  <div>
    <quotation-builder :items="items" :role="role" @update="onUpdate" />
    <a-space style="margin-top:12px">
      <a-button type="primary" @click="save">保存</a-button>
      <a-button @click="reload">刷新</a-button>
    </a-space>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import QuotationBuilder from '../../components/QuotationBuilder.vue'
import { getProjectBudget, batchUpdateBudget } from '../../api/modules/budgets'

const props = defineProps<{ projectId: string; role: any }>()
const items = ref<any[]>([])

async function reload() {
  const data = await getProjectBudget(props.projectId)
  const flat = (data.categories || []).flatMap((c: any) => c.items || [])
  items.value = flat
}

function onUpdate(next: any[]) { items.value = next }

async function save() { await batchUpdateBudget(props.projectId, items.value) }

onMounted(reload)
</script>

