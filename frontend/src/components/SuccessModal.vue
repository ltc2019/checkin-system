<script setup>
import { defineProps, defineEmits, computed } from 'vue'

const props = defineProps({
  show: Boolean,
  type: String, // 'early' | 'reading' | 'sport'
  message: String,
  points: Number
})

const emit = defineEmits(['close'])

const scenes = {
  early: [
    { emoji: '🌅', title: '早安！新的一天', desc: '早起的鸟儿有虫吃', bg: 'from-orange-400 to-pink-500' },
    { emoji: '☀️', title: '太阳升起', desc: '你比太阳更早醒来', bg: 'from-yellow-400 to-orange-500' },
    { emoji: '🌄', title: '迎接晨光', desc: '美好的一天从早起开始', bg: 'from-amber-400 to-red-400' },
    { emoji: '🐦', title: '晨鸟高飞', desc: '早起的人运气不会太差', bg: 'from-orange-300 to-yellow-400' },
  ],
  reading: [
    { emoji: '📖', title: '书香满溢', desc: '知识是最好的投资', bg: 'from-emerald-400 to-teal-500' },
    { emoji: '📚', title: '智慧增长', desc: '腹有诗书气自华', bg: 'from-green-400 to-emerald-500' },
    { emoji: '✨', title: '思想闪光', desc: '读书点亮人生', bg: 'from-teal-400 to-cyan-500' },
    { emoji: '🎓', title: '学无止境', desc: '每天进步一点点', bg: 'from-emerald-500 to-green-600' },
  ],
  sport: [
    { emoji: '💪', title: '活力满满', desc: '运动是最好的良药', bg: 'from-blue-400 to-cyan-500' },
    { emoji: '🏃', title: '奔跑向前', desc: '生命在于运动', bg: 'from-sky-400 to-blue-500' },
    { emoji: '🔥', title: '燃烧卡路里', desc: '坚持就是胜利', bg: 'from-orange-400 to-red-500' },
    { emoji: '⚡', title: '能量爆发', desc: '运动改变生活', bg: 'from-cyan-400 to-blue-500' },
  ]
}

const randomScene = computed(() => {
  const list = scenes[props.type] || scenes.early
  return list[Math.floor(Math.random() * list.length)]
})

const shareText = computed(() => {
  const typeNames = { early: '早起', reading: '读书', sport: '运动' }
  return `我今天完成了${typeNames[props.type] || ''}打卡！${randomScene.value.desc} #打卡签到`
})

const shareImage = computed(() => {
  // 返回场景图 URL（可以用 canvas 生成或预设图片）
  return null
})

const shareToWeibo = () => {
  const url = encodeURIComponent(window.location.href)
  const text = encodeURIComponent(shareText.value)
  window.open(`https://service.weibo.com/share/share.php?url=${url}&title=${text}`, '_blank')
}

const shareToQQ = () => {
  const url = encodeURIComponent(window.location.href)
  const text = encodeURIComponent(shareText.value)
  window.open(`https://connect.qq.com/widget/shareqq/index.html?url=${url}&title=${text}`, '_blank')
}

const shareToWechat = () => {
  // 微信分享需要调用微信 JS-SDK，这里提示用户
  alert('请截图后打开微信分享给好友')
}

const copyLink = () => {
  navigator.clipboard.writeText(shareText.value + ' ' + window.location.href)
  alert('已复制到剪贴板！')
}

const close = () => emit('close')
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="close">
        <!-- 背景遮罩 -->
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm"></div>

        <!-- 弹窗内容 -->
        <div class="relative w-full max-w-sm overflow-hidden rounded-3xl shadow-2xl">
          <!-- 场景图背景 -->
          <div :class="['relative p-8 text-center text-white bg-gradient-to-br', randomScene.bg]">
            <div class="text-7xl mb-4 animate-bounce">{{ randomScene.emoji }}</div>
            <h2 class="text-2xl font-bold mb-2">{{ randomScene.title }}</h2>
            <p class="text-white/90">{{ randomScene.desc }}</p>

            <!-- 装饰粒子 -->
            <div class="absolute top-4 left-4 w-2 h-2 bg-white/30 rounded-full animate-ping"></div>
            <div class="absolute top-12 right-8 w-3 h-3 bg-white/20 rounded-full animate-pulse"></div>
            <div class="absolute bottom-8 left-12 w-2 h-2 bg-white/25 rounded-full animate-ping"></div>
          </div>

          <!-- 成功信息 -->
          <div class="bg-white/10 backdrop-blur-xl p-6 text-center">
            <div class="text-white text-lg mb-2">{{ message }}</div>
            <div class="text-gradient text-2xl font-bold">+{{ points }} 积分</div>
          </div>

          <!-- 分享按钮 -->
          <div class="bg-white/5 backdrop-blur-xl p-4">
            <p class="text-white/60 text-sm text-center mb-3">分享到</p>
            <div class="flex justify-center gap-3">
              <button @click="shareToWeibo" class="w-12 h-12 rounded-full bg-red-500/20 hover:bg-red-500/40 flex items-center justify-center transition-all hover:scale-110">
                <span class="text-2xl">📱</span>
              </button>
              <button @click="shareToQQ" class="w-12 h-12 rounded-full bg-blue-500/20 hover:bg-blue-500/40 flex items-center justify-center transition-all hover:scale-110">
                <span class="text-2xl">💬</span>
              </button>
              <button @click="shareToWechat" class="w-12 h-12 rounded-full bg-green-500/20 hover:bg-green-500/40 flex items-center justify-center transition-all hover:scale-110">
                <span class="text-2xl">💚</span>
              </button>
              <button @click="copyLink" class="w-12 h-12 rounded-full bg-purple-500/20 hover:bg-purple-500/40 flex items-center justify-center transition-all hover:scale-110">
                <span class="text-2xl">🔗</span>
              </button>
            </div>
          </div>

          <!-- 关闭按钮 -->
          <button @click="close" class="absolute top-4 right-4 w-8 h-8 rounded-full bg-white/20 hover:bg-white/40 flex items-center justify-center text-white transition-all">
            ✕
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

.text-gradient {
  background: linear-gradient(135deg, #ffd700 0%, #ff8c00 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>