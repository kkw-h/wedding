<template>
  <a-table :dataSource="items" :columns="columns" rowKey="id" pagination="false" />
</template>

<script setup lang="ts">
import { computed, h } from 'vue'
import SensitiveText from './SensitiveText.vue'
import { InputNumber } from 'ant-design-vue'

interface Item { id: string; name: string; specs?: string; quantity: number; unit_price: number; cost_price?: number }
const props = defineProps<{ items: Item[]; role: 'ADMIN' | 'MANAGER' | 'PLANNER' | 'VENDOR' | 'FINANCE' }>()
const emit = defineEmits<{ (e: 'update', items: Item[]): void }>()

const columns = computed(() => [
  { title: '名称', dataIndex: 'name' },
  { title: '规格', dataIndex: 'specs' },
  { title: '数量', dataIndex: 'quantity', customRender: ({ record }: any) => h(InputNumber, { min: 1, value: record.quantity, onChange: (v: number) => update(record.id, { quantity: v }) }) },
  { title: '单价', dataIndex: 'unit_price', customRender: ({ record }: any) => h(InputNumber, { min: 0, value: record.unit_price, onChange: (v: number) => update(record.id, { unit_price: v }) }) },
  { title: '小计', key: 'total', customRender: ({ record }: any) => h(SensitiveText, { value: (record.quantity || 0) * (record.unit_price || 0) }) },
  ...(props.role === 'ADMIN' || props.role === 'MANAGER' ? [{ title: '成本', dataIndex: 'cost_price', customRender: ({ record }: any) => h(SensitiveText, { value: record.cost_price ?? 0 }) }] : [])
])

function update(id: string, patch: Partial<Item>) {
  const next = props.items.map(i => i.id === id ? { ...i, ...patch } : i)
  emit('update', next)
}
</script>
