<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const books = ref([])
const showForm = ref(false)
const editing = ref(null)
const title = ref('')
const author = ref('')
const totalPages = ref(0)
const currentPage = ref(0)
const error = ref('')

const fetchBooks = async () => {
  try {
    const res = await fetch('/api/books', {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    books.value = await res.json()
  } catch {}
}

const addBook = async () => {
  if (!title.value) { error.value = '请输入书名'; return }
  error.value = ''
  try {
    const res = await fetch('/api/books', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${userStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ title: title.value, author: author.value, total_pages: totalPages.value })
    })
    if (!res.ok) throw new Error('添加失败')
    showForm.value = false
    title.value = ''
    author.value = ''
    totalPages.value = 0
    fetchBooks()
  } catch {}
}

const updateProgress = async (book) => {
  try {
    await fetch(`/api/books/${book.id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${userStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        current_page: book.current_page,
        status: book.current_page >= book.total_pages ? 'finished' : 'reading'
      })
    })
    fetchBooks()
  } catch {}
}

const deleteBook = async (id) => {
  if (!confirm('确定删除？')) return
  try {
    await fetch(`/api/books/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    fetchBooks()
  } catch {}
}

onMounted(fetchBooks)
</script>

<template>
  <div class="p-4 max-w-lg mx-auto pb-24">
    <div class="card p-6 mb-4 gradient-knowledge">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div class="text-5xl">📚</div>
          <div>
            <h2 class="text-2xl font-bold text-white">书籍管理</h2>
            <p class="text-white/80 text-sm">记录阅读进度</p>
          </div>
        </div>
        <button @click="showForm = true" class="btn bg-white/20 text-white text-sm">+ 添加</button>
      </div>
    </div>

    <!-- Add Form -->
    <div v-if="showForm" class="card p-6 mb-4">
      <h3 class="font-bold mb-4">添加新书</h3>
      <div v-if="error" class="text-red-400 text-sm mb-2">{{ error }}</div>
      <input v-model="title" type="text" placeholder="书名" class="w-full mb-3" />
      <input v-model="author" type="text" placeholder="作者（选填）" class="w-full mb-3" />
      <input v-model.number="totalPages" type="number" placeholder="总页数（选填）" class="w-full mb-3" />
      <div class="flex gap-2">
        <button @click="addBook" class="btn gradient-knowledge text-white flex-1">添加</button>
        <button @click="showForm = false" class="btn bg-white/10 text-white/60">取消</button>
      </div>
    </div>

    <!-- Books List -->
    <div v-if="books.length === 0" class="card p-8 text-center">
      <div class="text-4xl mb-4 opacity-40">📖</div>
      <p class="text-white/40">还没有添加书籍</p>
      <button @click="showForm = true" class="text-primary mt-2">点击添加</button>
    </div>

    <div v-for="book in books" :key="book.id" class="card p-5 mb-3 card-hover">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <h3 class="font-bold text-lg">《{{ book.title }}》</h3>
          <p v-if="book.author" class="text-white/60 text-sm">{{ book.author }}</p>
          <div class="flex items-center gap-2 mt-2">
            <span class="text-xs text-white/40">进度:</span>
            <input
              type="number"
              v-model.number="book.current_page"
              @change="updateProgress(book)"
              min="0"
              :max="book.total_pages || 9999"
              class="w-16 text-sm py-1 px-2"
            />
            <span v-if="book.total_pages" class="text-xs text-white/40">/ {{ book.total_pages }} 页</span>
            <span
              class="text-xs px-2 py-1 rounded-full ml-auto"
              :class="book.status === 'finished' ? 'bg-green-500/30 text-green-300' : 'bg-yellow-500/30 text-yellow-300'"
            >
              {{ book.status === 'finished' ? '已读完' : '在读' }}
            </span>
          </div>
          <div v-if="book.total_pages" class="mt-3">
            <div class="h-2 bg-white/10 rounded-full overflow-hidden">
              <div
                class="h-full gradient-knowledge transition-all"
                :style="{ width: `${Math.min(100, (book.current_page / book.total_pages) * 100)}%` }"
              ></div>
            </div>
          </div>
        </div>
        <button @click="deleteBook(book.id)" class="text-red-400 text-sm hover:text-red-300 ml-4">删除</button>
      </div>
    </div>
  </div>
</template>