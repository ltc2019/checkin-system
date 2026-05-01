<script setup>
import { ref, onMounted, watch } from 'vue'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const period = ref('weekly')
const ranks = ref({ total: [], early: [], reading: [], sport: [] })
const activeTab = ref('total')
const loading = ref(false)

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

const getMedalEmoji = (i) => i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : ''
const getMedalClass = (i) => i === 0 ? 'medal-gold' : i === 1 ? 'medal-silver' : i === 2 ? 'medal-bronze' : 'text-white/40'
</script>

<template>
  <div class="p-4 max-w-lg mx-auto pb-24">
    <div class="card p-6 mb-4" style="background: linear-gradient(135deg, #ffd700 0%, #ff8c00 100%);">
      <div class="flex items-center gap-4">
        <div class="text-5xl animate-float">🏆</div>
        <div>
          <h2 class="text-2xl font-bold text-gray-800">排行榜</h2>
          <p class="text-gray-700 text-sm">看看谁是打卡达人</p>
        </div>
      </div>
    </div>

    <!-- Period Selector -->
    <div class="flex gap-2 mb-4">
      <button
        v-for="p in ['weekly', 'monthly', 'yearly']"
        :key="p"
        @click="period = p"
        class="btn flex-1 text-sm"
        :class="period === p ? 'bg-yellow-500/30 text-yellow-300' : 'bg-white/10 text-white/60'"
      >
        {{ p === 'weekly' ? '周榜' : p === 'monthly' ? '月榜' : '年榜' }}
      </button>
    </div>

    <!-- Tab Selector -->
    <div class="flex gap-2 mb-4">
      <button
        v-for="t in ['total', 'early', 'reading', 'sport']"
        :key="t"
        @click="activeTab = t"
        class="btn flex-1 text-sm"
        :class="activeTab === t ? 'gradient-primary text-white' : 'bg-white/10 text-white/60'"
      >
        {{ t === 'total' ? '总榜' : t === 'early' ? '早起' : t === 'reading' ? '读书' : '运动' }}
      </button>
    </div>

    <!-- Rank List -->
    <div class="card p-5">
      <div v-if="loading" class="text-center py-8 text-white/40">加载中...</div>
      <div v-else-if="ranks[activeTab].length === 0" class="text-center py-8 text-white/40">
        <div class="text-4xl mb-4 opacity-40">🏅</div>
        暂无排行数据
      </div>
      <div v-else>
        <div v-for="(r, i) in ranks[activeTab]" :key="r.id" class="flex items-center gap-3 py-3 border-b border-white/5 last:border-0">
          <div class="w-10 text-center text-xl" :class="getMedalClass(i)">
            {{ getMedalEmoji(i) || i + 1 }}
          </div>
          <div class="flex-1">
            <div class="font-bold">{{ r.nickname || '未命名' }}</div>
          </div>
          <div class="text-lg font-bold" :class="i < 3 ? 'text-gradient' : 'text-white/60'">
            {{ activeTab === 'total' ? r.period_score : r.count }} {{ activeTab === 'total' ? '分' : '次' }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>