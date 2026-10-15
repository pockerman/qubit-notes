import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// the backend serves /api; in development Vite forwards it there
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': process.env.STUDY_ASSISTANT_API_URL ?? 'http://localhost:8000',
    },
  },
})
