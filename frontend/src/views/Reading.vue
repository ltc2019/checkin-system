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
const showBookManager = ref(false)

// 添加书籍表单
const newBook = ref({ title: '', author: '', total_pages: 0 })
const editingBook = ref(null)

// 弹窗状态
const showModal = ref(false)
const modalMessage = ref('')
const modalPoints = ref(0)

// 录音
const isRecording = ref(false)
const mediaRecorder = ref(null)
const audioChunks = ref([])
const audioUrl = ref('')
const recordedFile = ref(null)
const micPermission = ref('unknown') // unknown | granted | denied | unsupported
const canRecord = ref(false) // 是否支持录音

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

// 检测录音支持情况
const checkRecordingSupport = () => {
  // HTTP 下 mediaDevices 不可用，只有 HTTPS 或 localhost 支持
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    canRecord.value = false
    micPermission.value = 'unsupported'

    // 检测是否是 HTTP 环境
    if (window.location.protocol === 'http:' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
      error.value = '录音功能需要 HTTPS 安全连接。请使用 localhost 或 HTTPS 地址访问，或上传预录音频文件'
    } else {
      error.value = '当前浏览器不支持录音功能，请上传预录音频文件'
    }
    return false
  }
  canRecord.value = true
  return true
}

// 检查麦克风权限
const checkMicPermission = async () => {
  if (!checkRecordingSupport()) return

  try {
    const result = await navigator.permissions.query({ name: 'microphone' })
    micPermission.value = result.state
  } catch {
    micPermission.value = 'unknown'
  }
}

// 请求麦克风权限
const requestMicPermission = async () => {
  if (!canRecord.value) {
    error.value = '录音功能需要 HTTPS 安全连接，请使用 localhost 访问或上传音频文件'
    return
  }

  error.value = ''
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    micPermission.value = 'granted'
    canRecord.value = true
    stream.getTracks().forEach(t => t.stop())
  } catch (err) {
    micPermission.value = 'denied'
    if (err.name === 'NotAllowedError') {
      error.value = '麦克风权限被拒绝，请在浏览器地址栏左侧点击允许，或上传音频文件'
    } else if (err.name === 'NotFoundError') {
      error.value = '未检测到麦克风设备，请上传音频文件'
    } else {
      error.value = '无法获取麦克风权限，请上传音频文件'
    }
  }
}

// 上传音频文件（替代方案）
const handleAudioUpload = async (e) => {
  const file = e.target.files[0]
  if (!file) return

  // 验证文件类型
  const validTypes = ['audio/webm', 'audio/mp4', 'audio/mpeg', 'audio/ogg', 'audio/wav', 'audio/m4a']
  if (!validTypes.includes(file.type) && !file.name.match(/\.(webm|mp3|m4a|wav|ogg|mp4)$/i)) {
    error.value = '请上传音频文件（mp3/m4a/wav/webm/ogg）'
    return
  }

  error.value = ''
  audioUrl.value = URL.createObjectURL(file)
  recordedFile.value = file
}

// 页面加载时检查权限
onMounted(async () => {
  await checkMicPermission()
  fetchBooks()
})

const startRecording = async () => {
  if (!canRecord.value) {
    error.value = '录音功能需要 HTTPS，请上传音频文件'
    return
  }

  // 先检查权限
  if (micPermission.value !== 'granted') {
    await requestMicPermission()
    if (micPermission.value !== 'granted') return
  }

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
    error.value = ''
  } catch (err) {
    micPermission.value = 'denied'
    error.value = '无法访问麦克风，请上传音频文件'
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

// 书籍管理
const addBook = async () => {
  if (!newBook.value.title.trim()) {
    error.value = '请输入书名'
    return
  }
  try {
    const res = await fetch('/api/books', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${userStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(newBook.value)
    })
    if (!res.ok) throw new Error('添加失败')
    newBook.value = { title: '', author: '', total_pages: 0 }
    error.value = ''
    await fetchBooks()
  } catch (e) {
    error.value = e.message
  }
}

const updateBookProgress = async (book) => {
  try {
    const maxPage = book.total_pages || 9999
    const page = Math.min(book.current_page, maxPage)
    await fetch(`/api/books/${book.id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${userStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        current_page: page,
        status: page >= book.total_pages && book.total_pages > 0 ? 'finished' : 'reading'
      })
    })
    await fetchBooks()
  } catch {}
}

const deleteBook = async (id) => {
  if (!confirm('确定删除这本书？')) return
  try {
    await fetch(`/api/books/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    await fetchBooks()
  } catch {}
}

const closeModal = () => { showModal.value = false }
</script>

<template>
  <div class="p-4 max-w-lg mx-auto pb-24">
    <div class="card p-6 mb-4 gradient-knowledge">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div class="text-5xl">📚</div>
          <div>
            <h2 class="text-2xl font-bold text-white">读书打卡</h2>
            <p class="text-white/80 text-sm">录音朗读 + 分享心得</p>
          </div>
        </div>
        <button
          @click="showBookManager = !showBookManager"
          class="btn bg-white/20 text-white text-sm"
        >
          {{ showBookManager ? '收起管理' : '📖 管理书籍' }}
        </button>
      </div>
    </div>

    <!-- 书籍管理面板 -->
    <div v-if="showBookManager" class="card p-5 mb-4">
      <h3 class="font-bold mb-4">我的书架</h3>

      <!-- 添加书籍 -->
      <div class="bg-white/5 rounded-xl p-4 mb-4">
        <div class="flex gap-2 mb-2">
          <input v-model="newBook.title" type="text" placeholder="书名" class="flex-1 text-sm py-2 px-3" />
        </div>
        <div class="flex gap-2 mb-2">
          <input v-model="newBook.author" type="text" placeholder="作者" class="flex-1 text-sm py-2 px-3" />
          <input v-model.number="newBook.total_pages" type="number" placeholder="总页数" class="w-24 text-sm py-2 px-3" />
        </div>
        <button @click="addBook" class="btn gradient-knowledge text-white text-sm py-2 px-6">
          + 添加书籍
        </button>
      </div>

      <!-- 书籍列表 -->
      <div v-if="books.length === 0" class="text-center py-6 text-white/40">
        还没有添加书籍，点击上方添加
      </div>
      <div v-for="book in books" :key="book.id" class="flex items-center gap-3 py-3 border-b border-white/5 last:border-0">
        <div class="flex-1 min-w-0">
          <div class="font-bold text-sm truncate">《{{ book.title }}》</div>
          <div class="text-white/40 text-xs">{{ book.author || '未设置作者' }}</div>
          <div class="flex items-center gap-2 mt-2">
            <input
              type="number"
              :value="book.current_page"
              @change="updateBookProgress(book)"
              min="0"
              class="w-16 text-sm py-1 px-2"
            />
            <span class="text-white/40 text-xs">/ {{ book.total_pages || '∞' }} 页</span>
            <span
              class="text-xs px-2 py-0.5 rounded-full"
              :class="book.status === 'finished' ? 'bg-green-500/30 text-green-300' : 'bg-yellow-500/30 text-yellow-300'"
            >
              {{ book.status === 'finished' ? '已读完' : '在读' }}
            </span>
          </div>
          <div v-if="book.total_pages" class="mt-2">
            <div class="h-1.5 bg-white/10 rounded-full overflow-hidden">
              <div
                class="h-full gradient-knowledge transition-all"
                :style="{ width: `${Math.min(100, (book.current_page / book.total_pages) * 100)}%` }"
              ></div>
            </div>
          </div>
        </div>
        <button @click="deleteBook(book.id)" class="text-red-400 text-xs hover:text-red-300 flex-shrink-0">删除</button>
      </div>
    </div>

    <!-- 打卡表单 -->
    <div class="card p-6">
      <div v-if="error" class="bg-red-500/20 border border-red-500/50 text-red-300 p-3 rounded-xl mb-4">
        <span>{{ error }}</span>
      </div>

      <!-- HTTPS/录音不支持提示 -->
      <div v-if="micPermission === 'unsupported'" class="bg-yellow-500/15 border border-yellow-500/40 p-4 rounded-xl mb-4">
        <div class="flex items-start gap-3">
          <span class="text-3xl flex-shrink-0">🔒</span>
          <div class="flex-1">
            <p class="text-yellow-300 font-bold text-sm">录音需要 HTTPS 安全连接</p>
            <p class="text-yellow-200/70 text-xs mt-1">
              HTTP 环境下浏览器禁止使用麦克风。请：
            </p>
            <ul class="text-yellow-200/70 text-xs mt-1 list-disc list-inside">
              <li>使用 http://localhost:3001 本地访问</li>
              <li>或配置 HTTPS 证书</li>
              <li>或上传预先录好的音频文件</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 麦克风权限被拒提示 -->
      <div v-else-if="micPermission === 'denied'" class="bg-yellow-500/15 border border-yellow-500/40 p-4 rounded-xl mb-4">
        <div class="flex items-center gap-3">
          <span class="text-3xl">🎤</span>
          <div class="flex-1">
            <p class="text-yellow-300 font-bold text-sm">需要麦克风权限</p>
            <p class="text-yellow-200/70 text-xs mt-1">点击浏览器地址栏左侧的图标允许麦克风，或上传音频文件</p>
          </div>
          <button
            @click="requestMicPermission"
            class="btn bg-yellow-500/30 text-yellow-200 text-sm py-2 px-4 flex-shrink-0"
          >
            重试授权
          </button>
        </div>
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
      </div>

      <!-- Reading Duration -->
      <div class="mb-4">
        <label class="text-white/60 text-sm mb-2 block">阅读时长（分钟）</label>
        <div class="flex items-center gap-4">
          <input type="range" v-model.number="duration" min="5" max="300" step="5" class="flex-1 accent-green-400" />
          <span class="text-lg font-bold" style="color: var(--knowledge-dark)">{{ duration }} 分钟</span>
        </div>
      </div>

      <!-- Audio Recording / Upload -->
      <div class="mb-4">
        <label class="text-white/60 text-sm mb-2 block">朗读录音（必填）</label>

        <!-- 录音按钮（仅在支持时显示） -->
        <div v-if="canRecord" class="flex items-center gap-4 mb-3">
          <button
            @click="isRecording ? stopRecording() : startRecording()"
            class="btn flex items-center gap-2"
            :class="[
              isRecording ? 'bg-red-500/30 text-red-300 animate-pulse' : 'gradient-knowledge text-white',
              micPermission === 'denied' ? 'opacity-50' : ''
            ]"
          >
            <span>{{ isRecording ? '⏹ 停止录音' : '🎙 开始录音' }}</span>
          </button>
          <span v-if="isRecording" class="text-red-400 animate-pulse">录音中...</span>
          <span v-else-if="micPermission === 'granted'" class="text-green-400 text-xs">✓ 已授权</span>
        </div>

        <!-- 上传音频文件（始终可用） -->
        <label class="flex items-center justify-center gap-2 p-4 border-2 border-dashed border-white/20 rounded-xl cursor-pointer hover:border-green-400/50 transition-all mb-3">
          <span class="text-2xl">📁</span>
          <span class="text-white/60 text-sm">{{ canRecord ? '或上传音频文件' : '上传音频文件（mp3/m4a/wav）' }}</span>
          <input type="file" accept="audio/*" @change="handleAudioUpload" class="hidden" />
        </label>

        <!-- 已录/已上传音频 -->
        <div v-if="audioUrl" class="mt-3">
          <audio :src="audioUrl" controls class="w-full" style="height: 40px;"></audio>
          <p class="text-green-400 text-xs mt-1">✓ 录音已就绪</p>
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