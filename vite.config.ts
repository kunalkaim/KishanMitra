import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    watch: {
      ignored: [
        '**/*.db',
        '**/*.db-wal',
        '**/*.db-shm',
        '**/*.sqlite3',
        '**/*.sqlite3-wal',
        '**/*.sqlite3-shm',
        '**/backend/**',
        '**/docs/**',
        '**/.git/**',
      ],
    },
  },
})
