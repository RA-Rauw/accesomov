import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: { port: 5173 },
  optimizeDeps: {
    // esbuild pre-bundlea mapbox-gl convirtiendo su formato UMD/CJS a ESM
    // con un default export correcto. Sin esto, `import mapboxgl` = undefined.
    include: ['mapbox-gl'],
  },
})
