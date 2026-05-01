<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useUserStore } from '../stores/user'
import { Line, Bar } from 'vue-chartjs'
import { Chart as ChartJS, registerables } from 'chart.js'
ChartJS.register(...registerables)

const userStore = useUserStore()
const period = ref('weekly')
const stats = ref({ by_type: {}, daily: {}, monthly: {}, total: 0 })
const loading = ref(false)

const isDark = computed(() => document.body.classList.contains('dark'))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { labels: { color: isDark.value ? 'rgba(255,255,255,0.8)' : '#1d1d1f', font: { size: 12 } } }
  },
  scales: {
    x: { ticks: { color: isDark.value ? 'rgba(255,255,255,0.6)' : '#86868b' }, grid: { color: isDark.value ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.06)' } },
    y: { ticks: { color: isDark.value ? 'rgba(255,255,255,0.6)' : '#86868b' }, grid: { color: isDark.value ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.06)' } }
  }
}))

const getChartData = () => {
  const data = period.value === 'yearly' ? stats.value.monthly : stats.value.daily
  const labels = Object.keys(data).sort()
  return {
    labels,
    datasets: [
      { label: '早起', data: labels.map(l => data[l]?.early || 0), borderColor: '#ff9500', backgroundColor: 'rgba(255, 149, 0, 0.15)', tension: 0.4, fill: true },
      { label: '读书', data: labels.map(l => data[l]?.reading || 0), borderColor: '#34c759', backgroundColor: 'rgba(52, 199, 89, 0.15)', tension: 0.4, fill: true },
      { label: '运动', data: labels.map(l => data[l]?.sport || 0), borderColor: '#007aff', backgroundColor: 'rgba(0, 122, 255, 0.15)', tension: 0.4, fill: true }
    ]
  }
}

const barChartData = () => {
  return {
    labels: ['早起', '读书', '运动'],
    datasets: [{
      data: [stats.value.by_type.early || 0, stats.value.by_type.reading || 0, stats.value.by_type.sport || 0],
      backgroundColor: ['#ff9500', '#34c759', '#007aff'],
      borderRadius: 8
    }]
  }
}

const fetchStats = async () => {
  loading.value = true
  try {
    const res = await fetch(`/api/stats/${period.value}`, {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    stats.value = await res.json()
  } catch {} finally {
    loading.value = false
  }
}

watch(period, fetchStats)
onMounted(fetchStats)
</script>

<template>
  <div class="p-4 max-w-lg mx-auto pb-24">
    <div class="card p-6 mb-4 gradient-primary">
      <div class="flex items-center gap-4">
        <div class="text-5xl">📊</div>
        <div>
          <h2 class="text-2xl font-bold text-white">统计分析</h2>
          <p class="text-white/80 text-sm">查看打卡数据趋势</p>
        </div>
      </div>
    </div>

    <div class="flex gap-2 mb-4">
      <button
        v-for="p in ['weekly', 'monthly', 'yearly']"
        :key="p"
        @click="period = p"
        class="btn flex-1 text-sm"
        :class="period === p ? 'btn-primary' : ''"
      >
        {{ p === 'weekly' ? '本周' : p === 'monthly' ? '本月' : '本年' }}
      </button>
    </div>

    <div class="card p-5 mb-4">
      <h3 class="font-bold mb-4 flex items-center gap-2">
        <span>📈</span> {{ period === 'weekly' ? '本周' : period === 'monthly' ? '本月' : '本年' }}概览
      </h3>
      <div class="grid grid-cols-4 gap-3">
        <div class="text-center">
          <div class="text-3xl font-bold text-gradient">{{ stats.total }}</div>
          <div class="text-xs text-secondary">总打卡</div>
        </div>
        <div class="text-center">
          <div class="text-3xl font-bold" style="color: var(--sunrise)">{{ stats.by_type.early || 0 }}</div>
          <div class="text-xs text-secondary">早起</div>
        </div>
        <div class="text-center">
          <div class="text-3xl font-bold" style="color: var(--knowledge)">{{ stats.by_type.reading || 0 }}</div>
          <div class="text-xs text-secondary">读书</div>
        </div>
        <div class="text-center">
          <div class="text-3xl font-bold" style="color: var(--sport)">{{ stats.by_type.sport || 0 }}</div>
          <div class="text-xs text-secondary">运动</div>
        </div>
      </div>
    </div>

    <div class="card p-5 mb-4">
      <h3 class="font-bold mb-4">单项统计</h3>
      <div style="height: 200px;">
        <Bar :data="barChartData()" :options="chartOptions" />
      </div>
    </div>

    <div class="card p-5">
      <h3 class="font-bold mb-4">趋势图表</h3>
      <div v-if="loading" class="text-center py-8 text-tertiary">加载中...</div>
      <div v-else style="height: 250px;">
        <Line :data="getChartData()" :options="chartOptions" />
      </div>
    </div>
  </div>
</template>