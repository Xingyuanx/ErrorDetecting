<template>
  <section class="layout__section">
    <div class="layout__page-header"><h2 class="layout__page-title">告警配置</h2></div>
    <div class="u-mb-2"><button class="btn" @click="open=true">新增规则</button></div>
    <table id="alert-rules-table" class="dashboard__table"><thead><tr><th>名称</th><th>条件</th><th>级别</th><th>渠道</th><th>操作</th></tr></thead><tbody id="alert-rules-tbody"><tr v-for="r in rules" :key="r.name" class="dashboard__table-row"><td>{{ r.name }}</td><td>{{ r.cond }}</td><td>{{ r.level }}</td><td>{{ r.channel }}</td><td><button class="btn u-text-sm" @click="edit(r)">编辑</button><button class="btn u-text-sm u-ml-1" @click="del(r.name)">删除</button></td></tr></tbody></table>
    <div v-show="open" class="u-mt-2">
      <form @submit.prevent="save">
        <input v-model.trim="form.name" placeholder="规则名" class="header__search-input" />
        <input v-model.trim="form.cond" placeholder="条件表达式" class="header__search-input" />
        <select v-model="form.level" class="header__search-input"><option>INFO</option><option>WARN</option><option>ERROR</option></select>
        <select v-model="form.channel" class="header__search-input"><option>EMAIL</option><option>SMS</option><option>WEBHOOK</option></select>
        <button class="btn">保存</button>
        <button class="btn u-ml-1" type="button" @click="open=false">取消</button>
      </form>
      <div class="u-text-sm u-text-gray-700">{{ err }}</div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
const rules = reactive<{ name:string; cond:string; level:string; channel:string }[]>([])
const open = ref(false)
const err = ref('')
const form = reactive({ name:'', cond:'', level:'INFO', channel:'EMAIL' })
function save() {
  if (!form.name || !form.cond) { err.value='请填写规则名称与条件'; return }
  if (rules.some(r => r.name===form.name)) { err.value='规则名称已存在'; return }
  rules.push({ name: form.name, cond: form.cond, level: form.level, channel: form.channel })
  err.value=''; open.value=false; form.name=''; form.cond=''
}
function del(n: string) { const i = rules.findIndex(r => r.name===n); if (i>=0) rules.splice(i,1) }
function edit(r: any) { open.value=true; form.name=r.name; form.cond=r.cond; form.level=r.level; form.channel=r.channel }
</script>

