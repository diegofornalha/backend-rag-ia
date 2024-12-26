import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'https://oraculo-api-latest.onrender.com',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path
      },
      '/health': {
        target: 'https://oraculo-api-latest.onrender.com',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
