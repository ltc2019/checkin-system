<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const username = ref('')
const password = ref('')
const nickname = ref('')
const isRegister = ref(false)
const error = ref('')
const loading = ref(false)

const submit = async () => {
  error.value = ''
  loading.value = true
  try {
    if (isRegister.value) {
      await userStore.register(username.value, password.value, nickname.value)
    } else {
      await userStore.login(username.value, password.value)
    }
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '操作失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <div class="card p-8 w-full max-w-md">
      <div class="text-center mb-8">
        <div class="text-6xl mb-4 animate-float">✨</div>
        <h1 class="text-3xl font-bold text-gradient">打卡签到系统</h1>
        <p class="text-white/60 mt-2">早起 · 读书 · 运动 · 遇见更好的自己</p>
      </div>

      <div v-if="error" class="bg-red-500/20 border border-red-500/50 text-red-300 p-3 rounded-xl mb-4">
        {{ error }}
      </div>

      <div class="space-y-4">
        <input v-model="username" type="text" placeholder="用户名" class="w-full" />
        <input v-model="password" type="password" placeholder="密码" class="w-full" />
        <input v-if="isRegister" v-model="nickname" type="text" placeholder="昵称" class="w-full" />

        <button
          @click="submit"
          :disabled="loading"
          class="btn gradient-primary text-white w-full text-lg"
        >
          {{ loading ? '请稍候...' : (isRegister ? '注册' : '登录') }}
        </button>

        <div class="text-center text-white/60">
          <button @click="isRegister = !isRegister" class="text-primary hover:underline">
            {{ isRegister ? '已有账号？去登录' : '没有账号？去注册' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>