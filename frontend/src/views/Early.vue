<script setup>
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '../stores/user'
import SuccessModal from '../components/SuccessModal.vue'

const userStore = useUserStore()
const notes = ref('')
const loading = ref(false)
const error = ref('')
const alreadyChecked = ref(false)
const currentTime = ref('')
const canCheckin = ref(false)

const showModal = ref(false)
const modalMessage = ref('')
const modalPoints = ref(0)
const modalAwards = ref([])

const buttonDisabled = computed(() => loading.value || alreadyChecked.value || !canCheckin.value)

const checkTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  const hour = now.getHours()
  const minute = now.getMinutes()
  const totalMinutes = hour * 60 + minute
  canCheckin.value = totalMinutes >= 330 && totalMinutes <= 510
}

const fetchToday = async () => {
  try {
    const res = await fetch('/api/checkin/today', {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    const data = await res.json()
    alreadyChecked.value = !!data.early
  } catch {}
}

const checkin = async () => {
  if (buttonDisabled.value) return
  loading.value = true
  error.value = ''
  try {
    const res = await fetch('/api/checkin/early', {
      method: 'POST',
      headers: { Authorization: `Bearer ${userStore.token}` },
      body: JSON.stringify({ notes: notes.value }),
    })
    const data = await res.json()
    if (!res.ok) {
      const errMsg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
      throw new Error(errMsg)
    }

    alreadyChecked.value = true
    modalMessage.value = data.message
    modalPoints.value = data.points || 2
    modalAwards.value = data.awards || []
    showModal.value = true
  } catch (e) {
    console.error('Early checkin error:', e)
    if (typeof e === 'string') {
      error.value = e
    } else if (e && e.message) {
      error.value = e.message
    } else if (e && e.detail) {
      error.value = e.detail
    } else {
      error.value = '打卡失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}

const closeModal = () => {
  showModal.value = false
}

onMounted(() => {
  checkTime()
  setInterval(checkTime, 1000)
  fetchToday()
})
</script>

<template>
  <div class="p-4 max-w-lg mx-auto pb-24">
    <div class="card p-6 mb-4 gradient-sunrise">
      <div class="flex items-center gap-4">
        <div class="text-5xl animate-float">🌅</div>
        <div>
          <h2 class="text-2xl font-bold text-white">早起打卡</h2>
          <p class="text-white/80 text-sm">打卡时间：5:30 - 8:30</p>
          <div class="text-3xl font-mono font-bold text-white mt-1">{{ currentTime }}</div>
        </div>
      </div>
    </div>

    <div class="card p-6">
      <div v-if="error" class="p-3 rounded-xl mb-4" style="background: rgba(255, 59, 48, 0.1); color: var(--danger);">
        {{ error }}
      </div>

      <div v-if="alreadyChecked" class="text-center py-8">
        <div class="text-6xl mb-4">✅</div>
        <h3 class="text-xl font-bold">今日已打卡</h3>
        <p class="text-secondary mt-2">明天继续保持！</p>
      </div>

      <div v-else-if="!canCheckin" class="text-center py-8">
        <div class="text-4xl mb-4 opacity-40">😴</div>
        <p class="text-tertiary">不在打卡时间范围内</p>
        <p class="text-tertiary text-sm mt-2">请等待 5:30 - 8:30 进行打卡</p>
      </div>

      <div v-else>
        <div class="mb-4">
          <label class="text-secondary text-sm mb-2 block">今日寄语（选填）</label>
          <textarea v-model="notes" rows="3" placeholder="记录今天的心情..." class="w-full resize-none"></textarea>
        </div>

        <button
          @click="checkin"
          :disabled="buttonDisabled"
          :class="[
            'btn w-full text-lg font-bold transition-all',
            buttonDisabled
              ? 'opacity-50 cursor-not-allowed'
              : 'gradient-sunrise text-white hover:scale-105'
          ]"
        >
          <span v-if="loading">打卡中...</span>
          <span v-else-if="alreadyChecked">已打卡 ✓</span>
          <span v-else>🌅 立即打卡</span>
        </button>
      </div>
    </div>

    <div class="card p-4 mt-4">
      <h4 class="font-bold text-sm mb-2 flex items-center gap-2">💡 打卡小贴士</h4>
      <ul class="text-tertiary text-sm space-y-1">
        <li>• 每天只能打卡一次</li>
        <li>• 连续打卡可获得额外积分</li>
        <li>• 早起打卡可获 2 积分</li>
      </ul>
    </div>

    <SuccessModal
      :show="showModal"
      type="early"
      :message="modalMessage"
      :points="modalPoints"
      :awards="modalAwards"
      @close="closeModal"
    />
  </div>
</template>