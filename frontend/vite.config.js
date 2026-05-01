import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import fs from 'fs'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 3001,
    https: true, // 自动生成自签名证书，支持麦克风录音
    proxy: {
      '/api': 'http://192.168.0.21:8000',
      '/uploads': 'http://192.168.0.21:8000'
    }
  }
})
