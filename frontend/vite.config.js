import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/transcribe': 'http://localhost:8000',
      '/format': 'http://localhost:8000',
    },
  },
})
