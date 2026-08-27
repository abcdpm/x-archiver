// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite' // 引入 v4 插件

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(), // 注册插件
  ],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/media': 'http://127.0.0.1:8000'
    }
  }
})