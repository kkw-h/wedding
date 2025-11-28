<template>
  <a-row gutter="16">
    <a-col :span="6"><a-card>本月签约额：<SensitiveText :value="123456" /></a-card></a-col>
    <a-col :span="6"><a-card>本月回款：<SensitiveText :value="654321" /></a-card></a-col>
    <a-col :span="6"><a-card>毛利率：<SensitiveText :value="45 + '%'" /></a-card></a-col>
    <a-col :span="6"><a-card>待办审批：3</a-card></a-col>
  </a-row>
</template>

<script setup lang="ts">
import SensitiveText from '../components/SensitiveText.vue'
</script>

