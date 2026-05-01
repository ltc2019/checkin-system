<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { useUserStore } from './stores/user'
import { computed } from 'vue'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.role === 'admin')
</script>

<template>
  <div class="min-h-screen pb-20">
    <RouterView />
    <nav v-if="userStore.token" class="fixed bottom-0 left-0 right-0 glass-nav">
      <div class="flex justify-around py-3">
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
        <RouterLink to="/stats" class="nav-item">
          <div class="nav-icon">📊</div>
          <div class="nav-text">统计</div>
        </RouterLink>
      </div>
      <div class="flex justify-center gap-8 py-2 border-t border-white/10">
        <RouterLink to="/rank" class="nav-item-sm">🏆 排行</RouterLink>
        <RouterLink v-if="isAdmin" to="/admin" class="nav-item-sm">⚙️ 管理</RouterLink>
        <button @click="userStore.logout()" class="nav-item-sm">🚪 退出</button>
      </div>
    </nav>
  </div>
</template>

<style scoped>
.glass-nav {
  background: rgba(15, 15, 35, 0.95);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 16px;
  border-radius: 12px;
  transition: all 0.2s;
}

.nav-item:hover, .nav-item.router-link-active {
  background: rgba(102, 126, 234, 0.2);
}

.nav-icon {
  font-size: 24px;
}

.nav-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}

.nav-item-sm {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  padding: 4px 12px;
  border-radius: 8px;
}

.nav-item-sm:hover, .nav-item-sm.router-link-active {
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}
</style>