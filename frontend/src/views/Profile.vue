<script setup>
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '../stores/user'
import { RouterLink } from 'vue-router'

const userStore = useUserStore()
const profile = ref(null)
const achievements = ref([])
const loading = ref(true)

const isAdmin = computed(() => userStore.role === 'admin')

const fetchProfile = async () => {
  try {
    const res = await fetch('/api/stats/profile', {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    profile.value = await res.json()
  } catch {}
}

const fetchAchievements = async () => {
  try {
    const res = await fetch('/api/achievements', {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    achievements.value = await res.json()
  } catch {}
}

const exportCSV = async () => {
  try {
    const res = await fetch('/api/export/csv', {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    const text = await res.text()
    const blob = new Blob([text], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'checkin_records.csv'
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    alert('导出失败')
  }
}

const exportJSON = async () => {
  try {
    const res = await fetch('/api/export/json', {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    const data = await res.json()
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'checkin_records.json'
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    alert('导出失败')
  }
}

const handleLogout = () => {
  userStore.logout()
  window.location.href = '/login'
}

onMounted(async () => {
  await Promise.all([fetchProfile(), fetchAchievements()])
  loading.value = false
})
</script>

<template>
  <div class="p-4 max-w-lg mx-auto pb-24">
    <!-- Profile Header -->
    <div class="card p-6 mb-4 gradient-primary">
      <div class="flex items-center gap-4">
        <div class="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center text-3xl text-white font-bold">
          {{ profile?.user?.nickname?.charAt(0) || profile?.user?.username?.charAt(0) || '?' }}
        </div>
        <div class="flex-1">
          <h2 class="text-xl font-bold text-white">{{ profile?.user?.nickname || profile?.user?.username || '' }}</h2>
          <p class="text-white/70 text-sm">@{{ profile?.user?.username || '' }}</p>
          <p class="text-white/50 text-xs mt-1">加入于 {{ profile?.user?.created_at?.slice(0, 10) || '' }}</p>
        </div>
      </div>
    </div>

    <!-- 功能入口 -->
    <div class="card p-5 mb-4">
      <div class="grid grid-cols-4 gap-3">
        <RouterLink to="/calendar" class="card p-4 text-center card-hover">
          <div class="text-2xl mb-1">📅</div>
          <div class="text-xs font-bold">日历</div>
        </RouterLink>
        <RouterLink to="/stats" class="card p-4 text-center card-hover">
          <div class="text-2xl mb-1">📊</div>
          <div class="text-xs font-bold">统计</div>
        </RouterLink>
        <RouterLink to="/history" class="card p-4 text-center card-hover">
          <div class="text-2xl mb-1">📜</div>
          <div class="text-xs font-bold">历史</div>
        </RouterLink>
        <RouterLink to="/rank" class="card p-4 text-center card-hover">
          <div class="text-2xl mb-1">🏆</div>
          <div class="text-xs font-bold">排行</div>
        </RouterLink>
      </div>
      <div v-if="isAdmin" class="mt-3">
        <RouterLink to="/admin" class="card p-4 text-center card-hover flex items-center justify-center gap-2">
          <span class="text-2xl">⚙️</span>
          <span class="text-sm font-bold">管理后台</span>
        </RouterLink>
      </div>
    </div>

    <div v-if="loading" class="text-center py-8 text-tertiary">加载中...</div>
    <template v-else-if="profile">
      <!-- Stats Overview -->
      <div class="card p-5 mb-4">
        <h3 class="font-bold mb-4 flex items-center gap-2">
          <span>📈</span> 打卡概览
        </h3>
        <div class="grid grid-cols-3 gap-4 mb-4">
          <div class="text-center">
            <div class="text-3xl font-bold text-gradient">{{ profile.current_streak }}</div>
            <div class="text-xs text-secondary mt-1">当前连续</div>
          </div>
          <div class="text-center">
            <div class="text-3xl font-bold" style="color: var(--gold)">{{ profile.max_streak }}</div>
            <div class="text-xs text-secondary mt-1">最长连续</div>
          </div>
          <div class="text-center">
            <div class="text-3xl font-bold text-gradient">{{ profile.total_points }}</div>
            <div class="text-xs text-secondary mt-1">总积分</div>
          </div>
        </div>

        <div class="grid grid-cols-3 gap-3">
          <div class="rounded-xl p-3 text-center tag-sunrise">
            <div class="text-xl font-bold">{{ profile.by_type.early }}</div>
            <div class="text-xs opacity-80">早起</div>
          </div>
          <div class="rounded-xl p-3 text-center tag-knowledge">
            <div class="text-xl font-bold">{{ profile.by_type.reading }}</div>
            <div class="text-xs opacity-80">读书</div>
          </div>
          <div class="rounded-xl p-3 text-center tag-sport">
            <div class="text-xl font-bold">{{ profile.by_type.sport }}</div>
            <div class="text-xs opacity-80">运动</div>
          </div>
        </div>
      </div>

      <!-- Achievements -->
      <div class="card p-5 mb-4">
        <h3 class="font-bold mb-4 flex items-center gap-2">
          <span>🏅</span> 我的成就
          <span class="ml-auto text-sm text-tertiary">{{ achievements.length }} 个</span>
        </h3>
        <div v-if="achievements.length === 0" class="text-center py-6 text-tertiary">
          <div class="text-4xl mb-2 opacity-50">🏅</div>
          <p class="text-sm">继续努力，解锁成就吧</p>
        </div>
        <div class="grid grid-cols-3 gap-3">
          <div v-for="a in achievements" :key="a.type" class="card p-3 text-center">
            <div class="text-2xl mb-1">{{ a.icon }}</div>
            <div class="text-xs font-bold leading-tight">{{ a.name }}</div>
            <div class="text-xs text-tertiary mt-1">{{ a.achieved_at?.slice(5, 10) }}</div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="card p-5 mb-4">
        <h3 class="font-bold mb-4 flex items-center gap-2">
          <span>🔧</span> 其他操作
        </h3>
        <div class="space-y-3">
          <button @click="exportCSV" class="btn w-full text-sm flex items-center justify-center gap-2">
            📥 导出打卡记录 (CSV)
          </button>
          <button @click="exportJSON" class="btn w-full text-sm flex items-center justify-center gap-2">
            📥 导出打卡记录 (JSON)
          </button>
          <button @click="handleLogout" class="btn w-full text-sm flex items-center justify-center gap-2" style="background: rgba(255, 59, 48, 0.1); color: var(--danger);">
            🚪 退出登录
          </button>
        </div>
      </div>
    </template>
  </div>
</template>