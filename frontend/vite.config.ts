import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // one shared .env at the repo root covers both frontend and backend
  envDir: '../',
})
