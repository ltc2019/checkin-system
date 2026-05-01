<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const calendar = ref({})
const year = ref(new Date().getFullYear())
const month = ref(new Date().getMonth() + 1)
const loading = ref(false)
const selectedDate = ref(null)
const selectedRecords = ref([])

const monthNames = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
const weekDays = ['日', '一', '二', '三', '四', '五', '六']

const daysInMonth = computed(() => {
  const days = []
  const firstDay = new Date(year.value, month.value - 1, 1).getDay()
  const totalDays = new Date(year.value, month.value, 0).getDate()

  for (let i = 0; i < firstDay; i++) {
    days.push({ day: null, date: null })
  }

  for (let d = 1; d <= totalDays; d++) {
    const dateStr = `${year.value}-${String(month.value).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    days.push({
      day: d,
      date: dateStr,
      data: calendar.value[dateStr] || { early: false, reading: false, sport: false }
    })
  }

  return days
})

const fetchCalendar = async () => {
  loading.value = true
  try {
    const res = await fetch(`/api/stats/calendar?year=${year.value}&month=${month.value}`, {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    const data = await res.json()
    calendar.value = data.calendar
  } catch {} finally {
    loading.value = false
  }
}

const prevMonth = () => {
  if (month.value === 1) {
    month.value = 12
    year.value--
  } else {
    month.value--
  }
}

const nextMonth = () => {
  if (month.value === 12) {
    month.value = 1
    year.value++
  } else {
    month.value++
  }
}

const goToToday = () => {
  year.value = new Date().getFullYear()
  month.value = new Date().getMonth() + 1
}

const selectDate = async (day) => {
  if (!day.date) return
  selectedDate.value = day.date
  selectedRecords.value = []
  if (day.data.early) selectedRecords.value.push({ type: 'early', time: '早起已打卡' })
  if (day.data.reading) selectedRecords.value.push({ type: 'reading', time: '读书已打卡' })
  if (day.data.sport) selectedRecords.value.push({ type: 'sport', time: '运动已打卡' })
}

const getTypeColor = (type) => {
  return type === 'early' ? 'color: var(--sunrise)' : type === 'reading' ? 'color: var(--knowledge)' : 'color: var(--sport)'
}

watch([year, month], fetchCalendar)
onMounted(fetchCalendar)
</script>

<template>
  <div class="p-4 max-w-lg mx-auto pb-24">
    <div class="card p-6 mb-4 gradient-primary">
      <div class="flex items-center gap-4">
        <div class="text-5xl">📅</div>
        <div>
          <h2 class="text-2xl font-bold text-white">打卡日历</h2>
          <p class="text-white/80 text-sm">一目了然，见证坚持</p>
        </div>
      </div>
    </div>

    <div class="card p-4 mb-4">
      <div class="flex items-center justify-between">
        <button @click="prevMonth" class="btn px-4">‹</button>
        <div class="text-center">
          <div class="text-xl font-bold">{{ year }}年 {{ monthNames[month - 1] }}</div>
          <button @click="goToToday" class="text-xs text-primary mt-1">回到今天</button>
        </div>
        <button @click="nextMonth" class="btn px-4">›</button>
      </div>
    </div>

    <div class="card p-4 mb-4">
      <div v-if="loading" class="text-center py-8 text-tertiary">加载中...</div>
      <template v-else>
        <div class="grid grid-cols-7 gap-1 mb-2">
          <div v-for="d in weekDays" :key="d" class="text-center text-xs text-tertiary py-2">{{ d }}</div>
        </div>

        <div class="grid grid-cols-7 gap-1">
          <div
            v-for="(day, i) in daysInMonth"
            :key="i"
            @click="selectDate(day)"
            class="aspect-square flex flex-col items-center justify-center rounded-lg cursor-pointer transition-all"
            :class="[
              day.day ? 'hover:bg-black/5 dark:hover:bg-white/5' : '',
              day.date === new Date().toISOString().slice(0, 10) ? 'ring-2 ring-primary' : '',
              selectedDate === day.date ? 'bg-primary/10 dark:bg-primary/20' : ''
            ]"
          >
            <span v-if="day.day" class="text-sm" :class="day.data.early || day.data.reading || day.data.sport ? 'font-bold' : 'text-tertiary'">
              {{ day.day }}
            </span>
            <div v-if="day.day && (day.data.early || day.data.reading || day.data.sport)" class="flex gap-0.5 mt-0.5">
              <span v-if="day.data.early" class="w-1.5 h-1.5 rounded-full" style="background: var(--sunrise)"></span>
              <span v-if="day.data.reading" class="w-1.5 h-1.5 rounded-full" style="background: var(--knowledge)"></span>
              <span v-if="day.data.sport" class="w-1.5 h-1.5 rounded-full" style="background: var(--sport)"></span>
            </div>
          </div>
        </div>

        <div class="flex justify-center gap-4 mt-4 pt-4" style="border-top: 1px solid var(--border)">
          <div class="flex items-center gap-1.5 text-xs text-secondary">
            <span class="w-2 h-2 rounded-full" style="background: var(--sunrise)"></span>早起
          </div>
          <div class="flex items-center gap-1.5 text-xs text-secondary">
            <span class="w-2 h-2 rounded-full" style="background: var(--knowledge)"></span>读书
          </div>
          <div class="flex items-center gap-1.5 text-xs text-secondary">
            <span class="w-2 h-2 rounded-full" style="background: var(--sport)"></span>运动
          </div>
        </div>
      </template>
    </div>

    <div v-if="selectedDate && selectedRecords.length > 0" class="card p-4">
      <h3 class="font-bold mb-3">{{ selectedDate }}</h3>
      <div v-for="r in selectedRecords" :key="r.type" class="flex items-center gap-2 py-2">
        <span class="text-xl">{{ r.type === 'early' ? '🌅' : r.type === 'reading' ? '📚' : '🏃' }}</span>
        <span :style="getTypeColor(r.type)">{{ r.time }}</span>
      </div>
    </div>
    <div v-else-if="selectedDate" class="card p-4 text-center text-tertiary">
      {{ selectedDate }} 暂无打卡记录
    </div>
  </div>
</template>