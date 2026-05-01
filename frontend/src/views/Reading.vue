<script setup>
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '../stores/user'
import SuccessModal from '../components/SuccessModal.vue'

const userStore = useUserStore()
const books = ref([])
const selectedBook = ref(null)
const notes = ref('')
const duration = ref(30)
const loading = ref(false)
const error = ref('')

// 弹窗状态
const showModal = ref(false)
const modalMessage = ref('')
const modalPoints = ref(0)

const isRecording = ref(false)
const mediaRecorder = ref(null)
const audioChunks = ref([])
const audioUrl = ref('')
const recordedFile = ref(null)

// 按钮是否可点击
const buttonDisabled = computed(() => loading.value || !recordedFile.value)

const fetchBooks = async () => {
  try {
    const res = await fetch('/api/books', {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    books.value = await res.json()
  } catch {}
}

const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder.value = new MediaRecorder(stream)
    audioChunks.value = []
    mediaRecorder.value.ondataavailable = (e) => audioChunks.value.push(e.data)
    mediaRecorder.value.onstop = () => {
      const blob = new Blob(audioChunks.value, { type: 'audio/webm' })
      audioUrl.value = URL.createObjectURL(blob)
      recordedFile.value = new File([blob], `reading_${Date.now()}.webm`, { type: 'audio/webm' })
      stream.getTracks().forEach(t => t.stop())
    }
    mediaRecorder.value.start()
    isRecording.value = true
  } catch {
    error.value = '无法访问麦克风'
  }
}

const stopRecording = () => {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop()
    isRecording.value = false
  }
}

const uploadAudio = async () => {
  if (!recordedFile.value) return null
  const formData = new FormData()
  formData.append('file', recordedFile.value)
  formData.append('folder', 'audio')
  const res = await fetch('/api/checkin/upload', {
    method: 'POST',
    headers: { Authorization: `Bearer ${userStore.token}` },
    body: formData
  })
  const data = await res.json()
  return data.url
}

const checkin = async () => {
  if (buttonDisabled.value) return
  loading.value = true
  error.value = ''
  try {
    const audioUrlResult = await uploadAudio()
    const res = await fetch('/api/checkin/reading', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${userStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        notes: notes.value,
        audio_url: audioUrlResult,
        book_id: selectedBook.value,
        reading_duration: duration.value
      })
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail)

    modalMessage.value = data.message
    modalPoints.value = data.points || 3
    showModal.value = true

    notes.value = ''
    selectedBook.value = null
    recordedFile.value = null
    audioUrl.value = ''
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const closeModal = () => { showModal.value = false }

onMounted(fetchBooks)
</script>

<template>
  <div class="p-4 max-w-lg mx-auto">
    <div class="card p-6 mb-4 gradient-knowledge">
      <div class="flex items-center gap-4">
        <div class="text-5xl">📚</div>
        <div>
          <h2 class="text-2xl font-bold text-white">读书打卡</h2>
          <p class="text-white/80 text-sm">录音朗读 + 分享心得</p>
        </div>
      </div>
    </div>

    <div class="card p-6">
      <div v-if="error" class="bg-red-500/20 border border-red-500/50 text-red-300 p-3 rounded-xl mb-4">
        {{ error }}
      </div>

      <!-- Select Book -->
      <div class="mb-4">
        <label class="text-white/60 text-sm mb-2 block">选择书籍（选填）</label>
        <select v-model="selectedBook" class="w-full bg-white/10 border border-white/30 rounded-xl p-3 text-white">
          <option value="" class="bg-gray-800">请选择书籍</option>
          <option v-for="book in books" :key="book.id" :value="book.id" class="bg-gray-800">
            《{{ book.title }}》{{ book.author ? ` - ${book.author}` : '' }}
          </option>
        </select>
        <a href="#/books" class="text-primary text-sm mt-1 inline-block">管理书籍</a>
      </div>

      <!-- Reading Duration -->
      <div class="mb-4">
        <label class="text-white/60 text-sm mb-2 block">阅读时长（分钟）</label>
        <div class="flex items-center gap-4">
          <input type="range" v-model.number="duration" min="5" max="300" step="5" class="flex-1 accent-green-400" />
          <span class="text-lg font-bold" style="color: var(--knowledge-dark)">{{ duration }} 分钟</span>
        </div>
      </div>

      <!-- Audio Recording -->
      <div class="mb-4">
        <label class="text-white/60 text-sm mb-2 block">朗读录音（必填）</label>
        <div class="flex items-center gap-4">
          <button
            @click="isRecording ? stopRecording() : startRecording()"
            class="btn flex items-center gap-2"
            :class="isRecording ? 'bg-red-500/30 text-red-300 animate-pulse' : 'gradient-knowledge text-white'"
          >
            <span>{{ isRecording ? '⏹ 停止录音' : '🎙 开始录音' }}</span>
          </button>
          <span v-if="isRecording" class="text-red-400 animate-pulse">录音中...</span>
        </div>
        <div v-if="audioUrl" class="mt-3">
          <audio :src="audioUrl" controls class="w-full" style="height: 40px;"></audio>
        </div>
      </div>

      <!-- Notes -->
      <div class="mb-4">
        <label class="text-white/60 text-sm mb-2 block">读书心得（选填）</label>
        <textarea v-model="notes" rows="4" placeholder="分享你的阅读感悟..." class="w-full resize-none"></textarea>
      </div>

      <button
        @click="checkin"
        :disabled="buttonDisabled"
        :class="[
          'btn w-full text-lg font-bold transition-all',
          buttonDisabled
            ? 'bg-gray-500/30 text-gray-400 cursor-not-allowed opacity-50'
            : 'gradient-knowledge text-white hover:scale-105'
        ]"
      >
        <span v-if="loading">提交中...</span>
        <span v-else>📚 提交打卡</span>
      </button>
    </div>

    <SuccessModal
      :show="showModal"
      type="reading"
      :message="modalMessage"
      :points="modalPoints"
      @close="closeModal"
    />
  </div>
</template>