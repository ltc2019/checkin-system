<script setup>
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '../stores/user'
import { RouterLink, useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()
const today = ref({ early: null, reading: [], sport: [] })
const stats = ref({ by_type: { early: 0, reading: 0, sport: 0 }, total: 0 })
const ranks = ref([])
const streak = ref({ early_streak: 0, total_streak: 0, max_streak: 0 })
const greeting = ref('')
const currentTime = ref('')
const loading = ref(true)

const checkinCount = computed(() => {
  let count = 0
  if (today.value.early) count++
  if (today.value.reading.length > 0) count++
  if (today.value.sport.length > 0) count++
  return count
})

const checkinProgress = computed(() => (checkinCount.value / 3) * 100)

const pendingCheckins = computed(() => {
  const pending = []
  if (!today.value.early) pending.push({ type: 'early', name: '早起', icon: '🌅', path: '/early' })
  if (today.value.reading.length === 0) pending.push({ type: 'reading', name: '读书', icon: '📚', path: '/reading' })
  if (today.value.sport.length === 0) pending.push({ type: 'sport', name: '运动', icon: '🏃', path: '/sport' })
  return pending
})

const fetchToday = async () => {
  try {
    const res = await fetch('/api/checkin/today', {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    today.value = await res.json()
  } catch {}
}

const fetchWeeklyStats = async () => {
  try {
    const res = await fetch('/api/stats/weekly', {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    stats.value = await res.json()
  } catch {}
}

const fetchRank = async () => {
  try {
    const res = await fetch('/api/stats/rank?period=weekly', {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    const data = await res.json()
    ranks.value = data.total.slice(0, 5)
  } catch {}
}

const fetchStreak = async () => {
  try {
    const res = await fetch('/api/stats/streak', {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    streak.value = await res.json()
  } catch {}
}

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  const hour = now.getHours()
  if (hour < 6) greeting.value = '夜深了，注意休息'
  else if (hour < 9) greeting.value = '早安，新的一天开始了'
  else if (hour < 12) greeting.value = '上午好，元气满满'
  else if (hour < 14) greeting.value = '中午好，记得休息'
  else if (hour < 18) greeting.value = '下午好，继续加油'
  else greeting.value = '晚上好，辛苦了一天'
}

onMounted(async () => {
  updateTime()
  setInterval(updateTime, 1000)
  loading.value = true
  await Promise.all([fetchToday(), fetchWeeklyStats(), fetchRank(), fetchStreak()])
  loading.value = false
})
</script>

<template>
  <div class="p-4 max-w-lg mx-auto pb-28">
    <!-- Header -->
    <div class="card p-6 mb-4 gradient-primary">
      <div class="flex justify-between items-start">
        <div>
          <p class="text-white/80 text-sm">{{ greeting }}</p>
          <h2 class="text-2xl font-bold mt-1 text-white">{{ userStore.user.nickname || userStore.user.username }}</h2>
          <div class="flex items-center gap-3 mt-2">
            <span class="text-sm text-white/80">🔥 连续 {{ streak.total_streak }} 天</span>
            <span class="text-sm text-yellow-300">最长 {{ streak.max_streak }} 天</span>
          </div>
        </div>
        <div class="text-right">
          <div class="text-3xl font-mono font-bold text-white">{{ currentTime }}</div>
          <p class="text-white/60 text-sm mt-1">{{ new Date().toLocaleDateString('zh-CN') }}</p>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-8 text-tertiary">加载中...</div>
    <template v-else>
      <!-- Quick Checkin -->
      <div v-if="pendingCheckins.length > 0" class="card p-5 mb-4">
        <h3 class="text-lg font-bold mb-3 flex items-center gap-2">
          <span>⚡</span> 快捷打卡
        </h3>
        <div class="flex gap-3">
          <RouterLink
            v-for="item in pendingCheckins"
            :key="item.type"
            :to="item.path"
            class="flex-1 card card-hover p-4 text-center"
            :class="'gradient-' + (item.type === 'early' ? 'sunrise' : item.type === 'reading' ? 'knowledge' : 'sport')"
          >
            <div class="text-2xl mb-1">{{ item.icon }}</div>
            <div class="text-xs font-bold text-white">{{ item.name }}</div>
          </RouterLink>
        </div>
      </div>

      <!-- Today Progress -->
      <div class="card p-5 mb-4">
        <h3 class="font-bold mb-4 flex items-center justify-between">
          <span class="flex items-center gap-2"><span>📋</span> 今日进度</span>
          <span class="text-gradient font-bold">{{ checkinCount }}/3</span>
        </h3>
        <div class="progress-bar mb-4">
          <div class="progress-fill" :style="{ width: checkinProgress + '%' }"></div>
        </div>
        <div class="grid grid-cols-3 gap-3">
          <RouterLink to="/early" class="card card-hover p-4 text-center" :class="today.early ? 'gradient-sunrise' : ''">
            <div class="text-2xl mb-1">{{ today.early ? '✅' : '🌅' }}</div>
            <div class="text-xs font-bold" :class="today.early ? 'text-white' : ''">{{ today.early ? '已打卡' : '早起' }}</div>
          </RouterLink>
          <RouterLink to="/reading" class="card card-hover p-4 text-center" :class="today.reading.length > 0 ? 'gradient-knowledge' : ''">
            <div class="text-2xl mb-1">{{ today.reading.length > 0 ? '✅' : '📚' }}</div>
            <div class="text-xs font-bold" :class="today.reading.length > 0 ? 'text-white' : ''">{{ today.reading.length > 0 ? '已打卡' : '读书' }}</div>
          </RouterLink>
          <RouterLink to="/sport" class="card card-hover p-4 text-center" :class="today.sport.length > 0 ? 'gradient-sport' : ''">
            <div class="text-2xl mb-1">{{ today.sport.length > 0 ? '✅' : '🏃' }}</div>
            <div class="text-xs font-bold" :class="today.sport.length > 0 ? 'text-white' : ''">{{ today.sport.length > 0 ? '已打卡' : '运动' }}</div>
          </RouterLink>
        </div>
      </div>

      <!-- Weekly Stats -->
      <div class="card p-5 mb-4">
        <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
          <span>📈</span> 本周统计
        </h3>
        <div class="grid grid-cols-4 gap-3">
          <div class="text-center">
            <div class="text-2xl font-bold text-gradient">{{ stats.total }}</div>
            <div class="text-xs text-secondary">总打卡</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold" style="color: var(--sunrise)">{{ stats.by_type.early || 0 }}</div>
            <div class="text-xs text-secondary">早起</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold" style="color: var(--knowledge)">{{ stats.by_type.reading || 0 }}</div>
            <div class="text-xs text-secondary">读书</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold" style="color: var(--sport)">{{ stats.by_type.sport || 0 }}</div>
            <div class="text-xs text-secondary">运动</div>
          </div>
        </div>
      </div>

      <!-- Mini Rank -->
      <div class="card p-5 mb-4">
        <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
          <span>🏆</span> 本周排行
          <RouterLink to="/rank" class="ml-auto text-sm text-primary">查看全部</RouterLink>
        </h3>
        <div v-if="ranks.length === 0" class="text-center py-4 text-tertiary">暂无数据</div>
        <div v-for="(r, i) in ranks" :key="r.id" class="flex items-center gap-3 py-3 border-b" style="border-color: var(--border)">
          <div class="text-xl w-8 text-center" :class="i < 3 ? '' : 'text-tertiary'">
            {{ i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : i + 1 }}
          </div>
          <div class="flex-1 font-medium">{{ r.nickname }}</div>
          <div class="text-gradient font-bold">{{ r.total }} 次</div>
        </div>
      </div>
    </template>
  </div>
</template>