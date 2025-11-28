<template>
  <span>{{ display }}</span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useUIStore } from '../stores/ui'

const props = defineProps<{ value: string | number; maskChar?: string }>()
const ui = useUIStore()
const display = computed(() => ui.isPresentationMode ? (props.maskChar ?? '*').repeat(6) : String(props.value ?? ''))
</script>

