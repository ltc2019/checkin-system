<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { useUserStore } from './stores/user'
import { computed, onMounted, ref } from 'vue'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.role === 'admin')
const isDark = ref(false)

const toggleTheme = () => {
  isDark.value = !isDark.value
  document.body.classList.toggle('dark', isDark.value)
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

onMounted(() => {
  const saved = localStorage.getItem('theme')
  isDark.value = saved === 'dark'
  document.body.classList.toggle('dark', isDark.value)
})
</script>

<template>
  <div class="min-h-screen">
    <!-- 主题切换按钮 -->
    <button
      v-if="userStore.token"
      @click="toggleTheme"
      class="theme-toggle"
    >
      {{ isDark ? '☀️' : '🌙' }}
    </button>

    <RouterView />
    <nav v-if="userStore.token" class="fixed-nav">
      <div class="flex justify-around py-2">
        <RouterLink to="/" class="nav-item">
          <div class="nav-icon">🏠</div>
          <div class="nav-text">首页</div>
        </RouterLink>
        <RouterLink to="/early" class="nav-item">
          <div class="nav-icon">🌅</div>
          <div class="nav-text">早起</div>
        </RouterLink>
        <RouterLink to="/reading" class="nav-item">
          <div class="nav-icon">📚</div>
          <div class="nav-text">读书</div>
        </RouterLink>
        <RouterLink to="/sport" class="nav-item">
          <div class="nav-icon">🏃</div>
          <div class="nav-text">运动</div>
        </RouterLink>
        <RouterLink to="/profile" class="nav-item">
          <div class="nav-icon">👤</div>
          <div class="nav-text">我的</div>
        </RouterLink>
      </div>
    </nav>
  </div>
</template>