<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../stores/user'
import SuccessModal from '../components/SuccessModal.vue'

const userStore = useUserStore()
const steps = ref(0)
const sportType = ref('跑步')
const calories = ref(0)
const notes = ref('')
const photoUrls = ref([])
const videoUrl = ref('')
const loading = ref(false)
const error = ref('')

// 弹窗状态
const showModal = ref(false)
const modalMessage = ref('')
const modalPoints = ref(0)

const sportTypes = ['跑步', '健身', '骑行', '游泳', '瑜伽', '篮球', '足球', '其他']

// 按钮是否可点击
const buttonDisabled = computed(() => loading.value || (photoUrls.value.length === 0 && !videoUrl.value))

const calcCalories = () => {
  const rate = { '跑步': 0.04, '骑行': 0.03, '游泳': 0.07, '健身': 0.05, '瑜伽': 0.025, '篮球': 0.06, '足球': 0.06, '其他': 0.035 }
  calories.value = Math.round(steps.value * 0.7 * (rate[sportType.value] || 0.035))
}

const handlePhotoUpload = async (e) => {
  const files = Array.from(e.target.files)
  for (const file of files) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('folder', 'photos')
    try {
      const res = await fetch('/api/checkin/upload', {
        method: 'POST',
        headers: { Authorization: `Bearer ${userStore.token}` },
        body: formData
      })
      const data = await res.json()
      photoUrls.value.push(data.url)
    } catch {}
  }
}

const handleVideoUpload = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  formData.append('folder', 'videos')
  try {
    const res = await fetch('/api/checkin/upload', {
      method: 'POST',
      headers: { Authorization: `Bearer ${userStore.token}` },
      body: formData
    })
    const data = await res.json()
    videoUrl.value = data.url
  } catch {}
}

const removePhoto = (index) => {
  photoUrls.value.splice(index, 1)
}

const checkin = async () => {
  if (buttonDisabled.value) return
  loading.value = true
  error.value = ''
  try {
    const res = await fetch('/api/checkin/sport', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${userStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        steps: steps.value,
        sport_type: sportType.value,
        calories: calories.value,
        notes: notes.value,
        photo_urls: JSON.stringify(photoUrls.value),
        video_url: videoUrl.value
      })
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail)

    modalMessage.value = data.message
    modalPoints.value = data.points || 3
    showModal.value = true

    steps.value = 0
    notes.value = ''
    photoUrls.value = []
    videoUrl.value = ''
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const closeModal = () => { showModal.value = false }
</script>

<template>
  <div class="p-4 max-w-lg mx-auto">
    <div class="card p-6 mb-4 gradient-sport">
      <div class="flex items-center gap-4">
        <div class="text-5xl">🏃</div>
        <div>
          <h2 class="text-2xl font-bold text-white">运动打卡</h2>
          <p class="text-white/80 text-sm">步数 + 拍照/视频记录</p>
        </div>
      </div>
    </div>

    <div class="card p-6">
      <div v-if="error" class="bg-red-500/20 border border-red-500/50 text-red-300 p-3 rounded-xl mb-4">
        {{ error }}
      </div>

      <!-- Sport Type -->
      <div class="mb-4">
        <label class="text-white/60 text-sm mb-2 block">运动类型</label>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="st in sportTypes"
            :key="st"
            @click="sportType = st"
            class="px-4 py-2 rounded-full text-sm font-medium transition-all"
            :class="sportType === st ? 'gradient-sport text-white' : 'bg-white/10 text-white/60 hover:bg-white/20'"
          >
            {{ st }}
          </button>
        </div>
      </div>

      <!-- Steps -->
      <div class="mb-4">
        <label class="text-white/60 text-sm mb-2 block">今日步数</label>
        <div class="flex items-center gap-4">
          <input type="number" v-model.number="steps" @input="calcCalories" placeholder="输入步数" class="w-full text-2xl font-bold" style="color: var(--sport-dark)" />
          <div class="text-right">
            <div class="text-sm text-white/40">预估消耗</div>
            <div class="text-lg font-bold" style="color: var(--sport-dark)">{{ calories }} 千卡</div>
          </div>
        </div>
      </div>

      <!-- Photo Upload -->
      <div class="mb-4">
        <label class="text-white/60 text-sm mb-2 block">拍照打卡（必填照片或视频）</label>
        <label class="flex items-center justify-center gap-2 p-6 border-2 border-dashed border-white/20 rounded-xl cursor-pointer hover:border-primary/50 transition-all">
          <span class="text-3xl">📷</span>
          <span class="text-white/60">点击上传照片</span>
          <input type="file" accept="image/*" multiple @change="handlePhotoUpload" class="hidden" />
        </label>
        <div v-if="photoUrls.length" class="flex flex-wrap gap-2 mt-3">
          <div v-for="(url, i) in photoUrls" :key="i" class="relative w-20 h-20 rounded-lg overflow-hidden">
            <img :src="url" class="w-full h-full object-cover" />
            <button @click="removePhoto(i)" class="absolute top-0 right-0 bg-red-500 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center">✕</button>
          </div>
        </div>
      </div>

      <!-- Video Upload -->
      <div class="mb-4">
        <label class="text-white/60 text-sm mb-2 block">视频打卡（选填）</label>
        <label class="flex items-center justify-center gap-2 p-4 border-2 border-dashed border-white/20 rounded-xl cursor-pointer hover:border-primary/50 transition-all">
          <span class="text-2xl">🎥</span>
          <span class="text-white/60">上传视频</span>
          <input type="file" accept="video/*" @change="handleVideoUpload" class="hidden" />
        </label>
        <video v-if="videoUrl" :src="videoUrl" controls class="w-full mt-3 rounded-xl" style="max-height: 200px;"></video>
      </div>

      <!-- Notes -->
      <div class="mb-4">
        <label class="text-white/60 text-sm mb-2 block">运动感悟（选填）</label>
        <textarea v-model="notes" rows="3" placeholder="记录今天的运动..." class="w-full resize-none"></textarea>
      </div>

      <button
        @click="checkin"
        :disabled="buttonDisabled"
        :class="[
          'btn w-full text-lg font-bold transition-all',
          buttonDisabled
            ? 'bg-gray-500/30 text-gray-400 cursor-not-allowed opacity-50'
            : 'gradient-sport text-white hover:scale-105'
        ]"
      >
        <span v-if="loading">提交中...</span>
        <span v-else>🏃 提交打卡</span>
      </button>
    </div>

    <SuccessModal
      :show="showModal"
      type="sport"
      :message="modalMessage"
      :points="modalPoints"
      @close="closeModal"
    />
  </div>
</template>