import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// the backend serves /api; in development Vite forwards it there
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': process.env.QUBIT_NOTES_API_URL ?? 'http://localhost:8001',
    },
  },
})
