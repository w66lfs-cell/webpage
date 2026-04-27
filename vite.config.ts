import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    allowedHosts: ['comedy-pig-insults.preview.emergentagent.com', 'comedy-pig-insults.cluster-5.preview.emergentcf.cloud', '.emergentagent.com', '.emergentcf.cloud'],
  },
})
