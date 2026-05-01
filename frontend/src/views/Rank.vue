<script setup>
import { ref, onMounted, watch } from 'vue'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const period = ref('weekly')
const ranks = ref({ total: [], early: [], reading: [], sport: [] })
const activeTab = ref('total')
const loading = ref(false)

const periods = [
  { key: 'daily', label: '日榜' },
  { key: 'weekly', label: '周榜' },
  { key: 'monthly', label: '月榜' },
  { key: 'yearly', label: '年榜' }
]

const tabs = [
  { key: 'total', label: '总榜', icon: '🏆' },
  { key: 'early', label: '早起', icon: '🌅' },
  { key: 'reading', label: '读书', icon: '📚' },
  { key: 'sport', label: '运动', icon: '🏃' }
]

const fetchRank = async () => {
  loading.value = true
  try {
    const res = await fetch(`/api/stats/rank?period=${period.value}`, {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    ranks.value = await res.json()
  } catch {} finally {
    loading.value = false
  }
}

watch(period, fetchRank)
onMounted(fetchRank)

const getMedal = (i) => i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : ''
</script>

<template>
  <div class="p-4 max-w-lg mx-auto pb-24">
    <div class="card p-6 mb-4 gradient-primary">
      <div class="flex items-center gap-4">
        <div class="text-5xl">🏆</div>
        <div>
          <h2 class="text-2xl font-bold text-white">排行榜</h2>
          <p class="text-white/80 text-sm">看看谁是打卡达人</p>
        </div>
      </div>
    </div>

    <div class="flex gap-2 mb-4">
      <button
        v-for="p in periods"
        :key="p.key"
        @click="period = p.key"
        class="btn flex-1 text-sm"
        :class="period === p.key ? 'btn-primary' : ''"
      >
        {{ p.label }}
      </button>
    </div>

    <div class="flex gap-2 mb-4">
      <button
        v-for="t in tabs"
        :key="t.key"
        @click="activeTab = t.key"
        class="btn flex-1 text-sm flex items-center justify-center gap-1"
        :class="activeTab === t.key ? (t.key === 'total' ? 'btn-primary' : t.key === 'early' ? 'gradient-sunrise text-white' : t.key === 'reading' ? 'gradient-knowledge text-white' : 'gradient-sport text-white') : ''"
      >
        <span>{{ t.icon }}</span>
        <span>{{ t.label }}</span>
      </button>
    </div>

    <div class="card p-5">
      <div v-if="loading" class="text-center py-8 text-tertiary">加载中...</div>
      <div v-else-if="!ranks[activeTab] || ranks[activeTab].length === 0" class="text-center py-8 text-tertiary">
        <div class="text-4xl mb-4 opacity-50">🏅</div>
        暂无排行数据
      </div>
      <div v-else>
        <div
          v-for="(r, i) in ranks[activeTab]"
          :key="r.id"
          class="flex items-center gap-3 py-3"
          style="border-bottom: 1px solid var(--border)"
        >
          <div class="w-10 text-center text-xl">
            <span v-if="i < 3">{{ getMedal(i) }}</span>
            <span v-else class="text-tertiary">{{ i + 1 }}</span>
          </div>
          <div class="flex-1">
            <div class="font-bold">{{ r.nickname }}</div>
            <div v-if="activeTab === 'total'" class="text-xs text-tertiary mt-0.5">
              🌅{{ r.early }} + 📚{{ r.reading }} + 🏃{{ r.sport }} = {{ r.total }}次
            </div>
          </div>
          <div class="text-right">
            <div class="font-bold" :class="i < 3 ? 'text-gradient' : 'text-secondary'">
              {{ activeTab === 'total' ? r.total : (activeTab === 'early' ? r.early : activeTab === 'reading' ? r.reading : r.sport) }}次
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>