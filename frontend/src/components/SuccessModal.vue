<script setup>
import { defineProps, defineEmits, computed, ref } from 'vue'

const props = defineProps({
  show: Boolean,
  type: String, // 'early' | 'reading' | 'sport'
  message: String,
  points: Number,
  awards: { type: Array, default: () => [] }
})

const emit = defineEmits(['close'])

const showQrCode = ref(false)
const shareChannel = ref('') // 'wechat' | 'wework' | 'moments'

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

const typeNames = { early: '早起', reading: '读书', sport: '运动' }

const shareText = computed(() => {
  return `🎉 我今天完成了${typeNames[props.type] || ''}打卡！${randomScene.value.desc} 已连续打卡多天，继续加油💪 #打卡签到 #自律人生`
})

const shareUrl = computed(() => {
  return window.location.origin
})

// 生成二维码URL（使用第三方服务）
const qrCodeUrl = computed(() => {
  const text = encodeURIComponent(shareText.value + '\n' + shareUrl.value)
  return `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${text}`
})

const shareToWeibo = () => {
  const url = encodeURIComponent(shareUrl.value)
  const text = encodeURIComponent(shareText.value)
  window.open(`https://service.weibo.com/share/share.php?url=${url}&title=${text}`, '_blank')
}

const shareToQQ = () => {
  const url = encodeURIComponent(shareUrl.value)
  const text = encodeURIComponent(shareText.value)
  window.open(`https://connect.qq.com/widget/shareqq/index.html?url=${url}&title=${text}`, '_blank')
}

// 企业微信分享 - 显示二维码让用户扫码后转发
const shareToWework = () => {
  shareChannel.value = 'wework'
  showQrCode.value = true
}

// 微信好友/群分享 - 显示二维码
const shareToWechat = () => {
  shareChannel.value = 'wechat'
  showQrCode.value = true
}

// 微信朋友圈分享 - 显示二维码
const shareToMoments = () => {
  shareChannel.value = 'moments'
  showQrCode.value = true
}

const copyShareText = async () => {
  try {
    await navigator.clipboard.writeText(shareText.value)
    alert('✓ 已复制分享内容！\n请打开微信/企业微信群粘贴发送')
  } catch {
    // 备用方案
    const textarea = document.createElement('textarea')
    textarea.value = shareText.value
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    alert('✓ 已复制分享内容！\n请打开微信/企业微信群粘贴发送')
  }
}

const closeQrCode = () => {
  showQrCode.value = false
  shareChannel.value = ''
}

const close = () => emit('close')

const getAchievementInfo = (award) => {
  const achievements = {
    early_7: { icon: '🌅', name: '早起坚持7天' },
    early_14: { icon: '🌅', name: '早起坚持14天' },
    early_30: { icon: '🌅', name: '早起坚持30天' },
    early_100: { icon: '🌅', name: '早起坚持100天' },
    reading_10: { icon: '📚', name: '读书10次' },
    reading_50: { icon: '📚', name: '读书50次' },
    reading_100: { icon: '📚', name: '读书100次' },
    reading_365: { icon: '📚', name: '读书365次' },
    sport_10: { icon: '🏃', name: '运动10次' },
    sport_50: { icon: '🏃', name: '运动50次' },
    sport_100: { icon: '🏃', name: '运动100次' },
    sport_365: { icon: '🏃', name: '运动365次' },
    all_1: { icon: '✨', name: '全能新人' },
    all_10: { icon: '✨', name: '全能达人10次' },
    all_50: { icon: '✨', name: '全能达人50次' },
    total_100: { icon: '🏆', name: '总打卡100次' },
    total_365: { icon: '🏆', name: '总打卡365次' },
    total_1000: { icon: '🏆', name: '总打卡1000次' },
  }
  return achievements[award] || { icon: '🏆', name: award }
}
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
          <div class="bg-white/10 backdrop-blur-xl p-6 text-center" style="background: var(--bg-secondary)">
            <div class="text-lg mb-2" style="color: var(--text)">{{ message }}</div>
            <div class="text-gradient text-2xl font-bold">+{{ points }} 积分</div>

            <!-- 新成就提示 -->
            <div v-if="awards && awards.length > 0" class="mt-4 pt-4" style="border-top: 1px solid var(--border)">
              <p class="font-bold text-sm mb-2 animate-bounce" style="color: var(--gold)">🎉 解锁新成就！</p>
              <div class="flex justify-center">
                <div class="rounded-xl px-4 py-2" style="background: rgba(255, 215, 0, 0.15); border: 1px solid rgba(255, 215, 0, 0.3)">
                  <span class="text-lg">{{ getAchievementInfo(awards[0]).icon }}</span>
                  <span class="text-sm font-bold ml-2" style="color: var(--gold)">{{ getAchievementInfo(awards[0]).name }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 分享按钮 -->
          <div class="p-4" style="background: var(--bg)">
            <p class="text-sm text-center mb-3" style="color: var(--text-secondary)">分享到</p>
            <div class="grid grid-cols-4 gap-3 mb-3">
              <!-- 企业微信 -->
              <button @click="shareToWework" class="aspect-square rounded-xl flex flex-col items-center justify-center transition-all hover:scale-105" style="background: rgba(0, 150, 136, 0.15)">
                <span class="text-2xl">🏢</span>
                <span class="text-xs mt-1" style="color: var(--text-secondary)">企业微信</span>
              </button>
              <!-- 微信好友/群 -->
              <button @click="shareToWechat" class="aspect-square rounded-xl flex flex-col items-center justify-center transition-all hover:scale-105" style="background: rgba(7, 193, 96, 0.15)">
                <span class="text-2xl">💚</span>
                <span class="text-xs mt-1" style="color: var(--text-secondary)">微信</span>
              </button>
              <!-- 朋友圈 -->
              <button @click="shareToMoments" class="aspect-square rounded-xl flex flex-col items-center justify-center transition-all hover:scale-105" style="background: rgba(7, 193, 96, 0.1)">
                <span class="text-2xl">🔄</span>
                <span class="text-xs mt-1" style="color: var(--text-secondary)">朋友圈</span>
              </button>
              <!-- 复制文本 -->
              <button @click="copyShareText" class="aspect-square rounded-xl flex flex-col items-center justify-center transition-all hover:scale-105" style="background: rgba(88, 86, 214, 0.15)">
                <span class="text-2xl">📋</span>
                <span class="text-xs mt-1" style="color: var(--text-secondary)">复制</span>
              </button>
            </div>
            <!-- 其他平台 -->
            <div class="flex justify-center gap-3">
              <button @click="shareToWeibo" class="w-10 h-10 rounded-full flex items-center justify-center transition-all hover:scale-110" style="background: rgba(229, 57, 53, 0.15)">
                <span class="text-xl">📱</span>
              </button>
              <button @click="shareToQQ" class="w-10 h-10 rounded-full flex items-center justify-center transition-all hover:scale-110" style="background: rgba(0, 122, 255, 0.15)">
                <span class="text-xl">💬</span>
              </button>
            </div>
          </div>

          <!-- 关闭按钮 -->
          <button @click="close" class="absolute top-4 right-4 w-8 h-8 rounded-full bg-white/20 hover:bg-white/40 flex items-center justify-center text-white transition-all">
            ✕
          </button>
        </div>

        <!-- 二维码弹窗 -->
        <Transition name="fade">
          <div v-if="showQrCode" class="absolute inset-0 z-60 flex items-center justify-center p-4" @click.self="closeQrCode">
            <div class="absolute inset-0 bg-black/40"></div>
            <div class="relative rounded-2xl p-6 w-72 text-center" style="background: var(--bg-secondary)">
              <div class="text-xl font-bold mb-2" style="color: var(--text)">
                {{ shareChannel === 'wework' ? '分享到企业微信' : shareChannel === 'wechat' ? '分享到微信' : '分享到朋友圈' }}
              </div>
              <p class="text-sm mb-4" style="color: var(--text-secondary)">
                长按识别二维码，转发给好友或群
              </p>
              <img :src="qrCodeUrl" class="w-48 h-48 mx-auto rounded-lg mb-4" alt="分享二维码" />
              <div class="text-xs mb-4 p-3 rounded-lg" style="background: var(--bg); color: var(--text-secondary)">
                {{ shareText }}
              </div>
              <div class="flex gap-2">
                <button @click="copyShareText" class="btn flex-1 text-sm">📋 复制文本</button>
                <button @click="closeQrCode" class="btn flex-1 text-sm">关闭</button>
              </div>
            </div>
          </div>
        </Transition>
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

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.text-gradient {
  background: linear-gradient(135deg, #ffd700 0%, #ff8c00 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>