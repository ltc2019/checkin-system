import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 3001,
    proxy: {
      '/api': 'http://192.168.0.21:8000',
      '/uploads': 'http://192.168.0.21:8000'
    }
  }
})
