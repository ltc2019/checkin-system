<script setup>
import { ref, onMounted, watch } from 'vue'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const records = ref([])
const total = ref(0)
const limit = ref(20)
const offset = ref(0)
const typeFilter = ref('')
const loading = ref(false)
const selectedRecord = ref(null)
const showModal = ref(false)

const typeNames = { early: '早起', reading: '读书', sport: '运动' }
const typeIcons = { early: '🌅', reading: '📚', sport: '🏃' }

const fetchHistory = async () => {
  loading.value = true
  try {
    const url = `/api/checkin/history?limit=${limit.value}&offset=${offset.value}${typeFilter.value ? '&type=' + typeFilter.value : ''}`
    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    const data = await res.json()
    records.value = data.records
    total.value = data.total
  } catch {} finally {
    loading.value = false
  }
}

const viewDetail = async (id) => {
  try {
    const res = await fetch(`/api/checkin/record/${id}`, {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    selectedRecord.value = await res.json()
    showModal.value = true
  } catch {}
}

const deleteRecord = async (id) => {
  if (!confirm('确定删除这条记录？')) return
  try {
    const res = await fetch(`/api/checkin/record/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    if (res.ok) {
      fetchHistory()
      showModal.value = false
    } else {
      const data = await res.json()
      alert(data.detail)
    }
  } catch {}
}

const formatDate = (dateStr) => {
  const d = new Date(dateStr)
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const canDelete = (record) => {
  const recordTime = new Date(record.checkin_time)
  return (Date.now() - recordTime.getTime()) < 24 * 60 * 60 * 1000
}

watch(typeFilter, () => {
  offset.value = 0
  fetchHistory()
})

onMounted(fetchHistory)
</script>

<template>
  <div class="p-4 max-w-lg mx-auto pb-24">
    <div class="card p-6 mb-4 gradient-primary">
      <div class="flex items-center gap-4">
        <div class="text-5xl">📜</div>
        <div>
          <h2 class="text-2xl font-bold text-white">打卡历史</h2>
          <p class="text-white/80 text-sm">共 {{ total }} 条记录</p>
        </div>
      </div>
    </div>

    <div class="flex gap-2 mb-4">
      <button
        @click="typeFilter = ''"
        class="btn flex-1 text-sm"
        :class="typeFilter === '' ? 'btn-primary' : ''"
      >
        全部
      </button>
      <button
        @click="typeFilter = 'early'"
        class="btn flex-1 text-sm"
        :class="typeFilter === 'early' ? 'gradient-sunrise text-white' : ''"
      >
        🌅 早起
      </button>
      <button
        @click="typeFilter = 'reading'"
        class="btn flex-1 text-sm"
        :class="typeFilter === 'reading' ? 'gradient-knowledge text-white' : ''"
      >
        📚 读书
      </button>
      <button
        @click="typeFilter = 'sport'"
        class="btn flex-1 text-sm"
        :class="typeFilter === 'sport' ? 'gradient-sport text-white' : ''"
      >
        🏃 运动
      </button>
    </div>

    <div class="card p-4">
      <div v-if="loading" class="text-center py-8 text-tertiary">加载中...</div>
      <div v-else-if="records.length === 0" class="text-center py-8 text-tertiary">
        <div class="text-4xl mb-4 opacity-50">📭</div>
        暂无打卡记录
      </div>
      <div v-else>
        <div
          v-for="r in records"
          :key="r.id"
          @click="viewDetail(r.id)"
          class="flex items-center gap-3 py-3 cursor-pointer rounded-lg px-2 -mx-2 hover:bg-black/5 dark:hover:bg-white/5"
          style="border-bottom: 1px solid var(--border)"
        >
          <div class="text-2xl">{{ typeIcons[r.type] }}</div>
          <div class="flex-1 min-w-0">
            <div class="font-bold text-sm">{{ typeNames[r.type] }}</div>
            <div class="text-xs text-tertiary">{{ formatDate(r.checkin_time) }}</div>
          </div>
          <div class="text-xs text-tertiary">
            <span v-if="r.notes" class="mr-2">📝</span>
            <span v-if="r.steps">🏃{{ r.steps }}步</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showModal && selectedRecord" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4" @click.self="showModal = false">
      <div class="card p-6 w-full max-w-md">
        <div class="flex items-center gap-3 mb-4">
          <div class="text-3xl">{{ typeIcons[selectedRecord.type] }}</div>
          <div>
            <h3 class="font-bold text-lg">{{ typeNames[selectedRecord.type] }}</h3>
            <p class="text-sm text-tertiary">{{ formatDate(selectedRecord.checkin_time) }}</p>
          </div>
        </div>

        <div class="space-y-3 text-sm">
          <div v-if="selectedRecord.notes">
            <span class="text-secondary">备注：</span>
            <span>{{ selectedRecord.notes }}</span>
          </div>
          <div v-if="selectedRecord.steps">
            <span class="text-secondary">步数：</span>
            <span>{{ selectedRecord.steps }} 步</span>
          </div>
          <div v-if="selectedRecord.calories">
            <span class="text-secondary">消耗：</span>
            <span>{{ selectedRecord.calories }} 千卡</span>
          </div>
          <div v-if="selectedRecord.sport_type">
            <span class="text-secondary">运动类型：</span>
            <span>{{ selectedRecord.sport_type }}</span>
          </div>
          <div v-if="selectedRecord.reading_duration">
            <span class="text-secondary">阅读时长：</span>
            <span>{{ selectedRecord.reading_duration }} 分钟</span>
          </div>
          <div v-if="selectedRecord.audio_url">
            <span class="text-secondary">录音：</span>
            <audio :src="selectedRecord.audio_url" controls class="w-full mt-1" style="height: 32px;"></audio>
          </div>
          <div v-if="selectedRecord.photo_urls">
            <span class="text-secondary block mb-2">照片：</span>
            <div class="flex flex-wrap gap-2">
              <img v-for="(url, i) in JSON.parse(selectedRecord.photo_urls || '[]')" :key="i" :src="url" class="w-20 h-20 rounded-lg object-cover" />
            </div>
          </div>
        </div>

        <div class="flex gap-2 mt-6">
          <button @click="showModal = false" class="btn flex-1">关闭</button>
          <button
            v-if="canDelete(selectedRecord)"
            @click="deleteRecord(selectedRecord.id)"
            class="btn flex-1"
            style="background: rgba(255, 59, 48, 0.1); color: var(--danger);"
          >
            删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>