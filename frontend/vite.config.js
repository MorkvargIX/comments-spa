import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost',
        ws: true,
      },
    },
  },
  plugins: [
    vue(),
    tailwindcss(),
  ],
})