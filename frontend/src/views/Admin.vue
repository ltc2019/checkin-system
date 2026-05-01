<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const users = ref([])
const rules = ref([])
const showAddUser = ref(false)
const showEditUser = ref(null)
const username = ref('')
const password = ref('')
const nickname = ref('')
const role = ref('member')
const error = ref('')

const fetchUsers = async () => {
  try {
    const res = await fetch('/api/admin/users', {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    users.value = await res.json()
  } catch {}
}

const fetchRules = async () => {
  try {
    const res = await fetch('/api/admin/rules', {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    rules.value = await res.json()
  } catch {}
}

const addUser = async () => {
  if (!username.value || !password.value || !nickname.value) {
    error.value = '请填写完整信息'
    return
  }
  error.value = ''
  try {
    const res = await fetch('/api/admin/users', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${userStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: username.value,
        password: password.value,
        nickname: nickname.value,
        role: role.value
      })
    })
    if (!res.ok) throw new Error('添加失败')
    showAddUser.value = false
    username.value = ''
    password.value = ''
    nickname.value = ''
    fetchUsers()
  } catch {}
}

const deleteUser = async (id) => {
  if (!confirm('确定删除？')) return
  try {
    await fetch(`/api/admin/users/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    fetchUsers()
  } catch {}
}

const updateRule = async (rule) => {
  try {
    await fetch(`/api/admin/rules/${rule.type}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${userStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        start_time: rule.start_time,
        end_time: rule.end_time,
        min_steps: rule.min_steps,
        required_media: rule.required_media,
        points: rule.points,
        enabled: rule.enabled
      })
    })
    fetchRules()
  } catch {}
}

const activeSection = ref('users')

onMounted(() => {
  fetchUsers()
  fetchRules()
})
</script>

<template>
  <div class="p-4 max-w-lg mx-auto">
    <div class="card p-6 mb-4 gradient-primary">
      <div class="flex items-center gap-4">
        <div class="text-5xl">⚙️</div>
        <div>
          <h2 class="text-2xl font-bold text-white">管理后台</h2>
          <p class="text-white/80 text-sm">人员管理 · 规则配置</p>
        </div>
      </div>
    </div>

    <!-- Section Tabs -->
    <div class="flex gap-2 mb-4">
      <button
        @click="activeSection = 'users'"
        class="btn flex-1 text-sm"
        :class="activeSection === 'users' ? 'gradient-primary text-white' : 'bg-white/10 text-white/60'"
      >
        👥 人员管理
      </button>
      <button
        @click="activeSection = 'rules'"
        class="btn flex-1 text-sm"
        :class="activeSection === 'rules' ? 'gradient-primary text-white' : 'bg-white/10 text-white/60'"
      >
        📋 打卡规则
      </button>
    </div>

    <!-- Users Section -->
    <div v-if="activeSection === 'users'">
      <div class="card p-4 mb-4 flex justify-between items-center">
        <h3 class="font-bold">用户列表 ({{ users.length }})</h3>
        <button @click="showAddUser = true" class="btn bg-white/20 text-white text-sm">+ 添加用户</button>
      </div>

      <!-- Add User Form -->
      <div v-if="showAddUser" class="card p-6 mb-4">
        <h3 class="font-bold mb-4">添加新用户</h3>
        <div v-if="error" class="text-red-400 text-sm mb-2">{{ error }}</div>
        <input v-model="username" type="text" placeholder="用户名" class="w-full mb-3" />
        <input v-model="password" type="password" placeholder="密码" class="w-full mb-3" />
        <input v-model="nickname" type="text" placeholder="昵称" class="w-full mb-3" />
        <select v-model="role" class="w-full mb-3 bg-white/10 border border-white/30 rounded-xl p-3 text-white">
          <option value="member" class="bg-gray-800">普通成员</option>
          <option value="admin" class="bg-gray-800">管理员</option>
        </select>
        <div class="flex gap-2">
          <button @click="addUser" class="btn gradient-primary text-white flex-1">添加</button>
          <button @click="showAddUser = false" class="btn bg-white/10 text-white/60">取消</button>
        </div>
      </div>

      <!-- Users List -->
      <div v-for="user in users" :key="user.id" class="card p-4 mb-3">
        <div class="flex items-center justify-between">
          <div>
            <div class="font-bold">{{ user.nickname || user.username }}</div>
            <div class="text-xs text-white/40">@{{ user.username }}</div>
            <span
              class="text-xs px-2 py-1 rounded-full mt-1 inline-block"
              :class="user.role === 'admin' ? 'bg-primary/30 text-primary' : 'bg-white/10 text-white/60'"
            >
              {{ user.role === 'admin' ? '管理员' : '成员' }}
            </span>
          </div>
          <button @click="deleteUser(user.id)" class="text-red-400 text-sm hover:text-red-300">删除</button>
        </div>
      </div>
    </div>

    <!-- Rules Section -->
    <div v-if="activeSection === 'rules'">
      <div class="card p-4 mb-4">
        <h3 class="font-bold">打卡规则配置</h3>
      </div>

      <div v-for="rule in rules" :key="rule.type" class="card p-5 mb-3">
        <h3 class="font-bold mb-4 flex items-center gap-2">
          <span class="text-xl">{{ rule.type === 'early' ? '🌅' : rule.type === 'reading' ? '📚' : '🏃' }}</span>
          {{ rule.type === 'early' ? '早起规则' : rule.type === 'reading' ? '读书规则' : '运动规则' }}
          <span
            class="ml-auto text-xs px-2 py-1 rounded-full"
            :class="rule.enabled ? 'bg-green-500/30 text-green-300' : 'bg-red-500/30 text-red-300'"
          >
            {{ rule.enabled ? '启用' : '禁用' }}
          </span>
        </h3>

        <div class="space-y-3">
          <div v-if="rule.type === 'early'" class="flex items-center gap-2">
            <label class="text-white/60 text-sm">打卡时间:</label>
            <input v-model="rule.start_time" type="text" placeholder="05:30" class="flex-1 text-sm py-1" />
            <span class="text-white/40">-</span>
            <input v-model="rule.end_time" type="text" placeholder="08:30" class="flex-1 text-sm py-1" />
          </div>

          <div v-if="rule.type === 'sport'" class="flex items-center gap-2">
            <label class="text-white/60 text-sm">最少步数:</label>
            <input v-model.number="rule.min_steps" type="number" class="flex-1 text-sm py-1" />
          </div>

          <div v-if="rule.type !== 'early'" class="flex items-center gap-2">
            <label class="text-white/60 text-sm">必填内容:</label>
            <input v-model="rule.required_media" type="text" placeholder="audio/photo/video" class="flex-1 text-sm py-1" />
          </div>

          <div class="flex items-center gap-2">
            <label class="text-white/60 text-sm">积分奖励:</label>
            <input v-model.number="rule.points" type="number" class="flex-1 text-sm py-1" />
          </div>

          <div class="flex items-center gap-2">
            <label class="text-white/60 text-sm">状态:</label>
            <button
              @click="rule.enabled = rule.enabled ? 0 : 1"
              class="btn text-sm"
              :class="rule.enabled ? 'bg-green-500/30 text-green-300' : 'bg-red-500/30 text-red-300'"
            >
              {{ rule.enabled ? '启用' : '禁用' }}
            </button>
          </div>

          <button @click="updateRule(rule)" class="btn gradient-primary text-white w-full text-sm mt-2">
            保存修改
          </button>
        </div>
      </div>
    </div>
  </div>
</template>