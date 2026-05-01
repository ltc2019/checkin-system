<script setup>
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '../stores/user'
import { RouterLink } from 'vue-router'

const userStore = useUserStore()
const today = ref({ early: null, reading: [], sport: [] })
const stats = ref({ by_type: { early: 0, reading: 0, sport: 0 }, total: 0 })
const ranks = ref([])
const greeting = ref('')
const currentTime = ref('')

const checkinCount = computed(() => {
  let count = 0
  if (today.value.early) count++
  if (today.value.reading.length > 0) count++
  if (today.value.sport.length > 0) count++
  return count
})

const streak = computed(() => {
  if (!today.value.early) return 0
  return Math.floor(Math.random() * 30) + 1
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

onMounted(() => {
  updateTime()
  setInterval(updateTime, 1000)
  fetchToday()
  fetchWeeklyStats()
  fetchRank()
})
</script>

<template>
  <div class="p-4 max-w-lg mx-auto pb-24">
    <!-- Header -->
    <div class="card p-6 mb-4 gradient-primary">
      <div class="flex justify-between items-start">
        <div>
          <p class="text-white/80 text-sm">{{ greeting }}</p>
          <h2 class="text-2xl font-bold mt-1">{{ userStore.user.nickname || userStore.user.username }}</h2>
        </div>
        <div class="text-right">
          <div class="text-3xl font-mono font-bold">{{ currentTime }}</div>
          <p class="text-white/60 text-sm mt-1">{{ new Date().toLocaleDateString('zh-CN') }}</p>
        </div>
      </div>
    </div>

    <!-- Today Status -->
    <div class="card p-5 mb-4">
      <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
        <span class="text-xl">📋</span> 今日打卡
        <span class="ml-auto text-gradient font-bold">{{ checkinCount }}/3</span>
      </h3>
      <div class="grid grid-cols-3 gap-3">
        <RouterLink to="/early" class="card-hover card p-4 text-center" :class="today.early ? 'gradient-sunrise' : ''">
          <div class="text-3xl mb-2">{{ today.early ? '✅' : '🌅' }}</div>
          <div class="text-sm font-bold">{{ today.early ? '已打卡' : '早起' }}</div>
          <div class="text-xs mt-1 opacity-80">5:30-8:30</div>
        </RouterLink>
        <RouterLink to="/reading" class="card-hover card p-4 text-center" :class="today.reading.length > 0 ? 'gradient-knowledge' : ''">
          <div class="text-3xl mb-2">{{ today.reading.length > 0 ? '✅' : '📚' }}</div>
          <div class="text-sm font-bold">{{ today.reading.length > 0 ? '已打卡' : '读书' }}</div>
          <div class="text-xs mt-1 opacity-80">录音+心得</div>
        </RouterLink>
        <RouterLink to="/sport" class="card-hover card p-4 text-center" :class="today.sport.length > 0 ? 'gradient-sport' : ''">
          <div class="text-3xl mb-2">{{ today.sport.length > 0 ? '✅' : '🏃' }}</div>
          <div class="text-sm font-bold">{{ today.sport.length > 0 ? '已打卡' : '运动' }}</div>
          <div class="text-xs mt-1 opacity-80">拍照打卡</div>
        </RouterLink>
      </div>
    </div>

    <!-- Weekly Stats -->
    <div class="card p-5 mb-4">
      <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
        <span class="text-xl">📈</span> 本周统计
      </h3>
      <div class="grid grid-cols-4 gap-3">
        <div class="text-center">
          <div class="text-2xl font-bold text-gradient">{{ stats.total }}</div>
          <div class="text-xs text-white/60">总打卡</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold" style="color: var(--sunrise)">{{ stats.by_type.early || 0 }}</div>
          <div class="text-xs text-white/60">早起</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold" style="color: var(--knowledge)">{{ stats.by_type.reading || 0 }}</div>
          <div class="text-xs text-white/60">读书</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold" style="color: var(--sport)">{{ stats.by_type.sport || 0 }}</div>
          <div class="text-xs text-white/60">运动</div>
        </div>
      </div>
    </div>

    <!-- Mini Rank -->
    <div class="card p-5">
      <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
        <span class="text-xl">🏆</span> 本周排行
        <RouterLink to="/rank" class="ml-auto text-sm text-primary">查看全部</RouterLink>
      </h3>
      <div v-if="ranks.length === 0" class="text-center text-white/40 py-4">暂无数据</div>
      <div v-for="(r, i) in ranks" :key="r.id" class="flex items-center gap-3 py-2 border-b border-white/5 last:border-0">
        <div class="text-xl w-8 text-center" :class="i === 0 ? 'medal-gold' : i === 1 ? 'medal-silver' : i === 2 ? 'medal-bronze' : 'text-white/40'">
          {{ i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : i + 1 }}
        </div>
        <div class="flex-1 font-medium">{{ r.nickname }}</div>
        <div class="text-gradient font-bold">{{ r.period_score }} 分</div>
      </div>
    </div>
  </div>
</template>