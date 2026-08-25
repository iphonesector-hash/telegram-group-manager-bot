import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const SECTOR_ASSET_ALIASES = new Map([
  ['/assets/sector/brand-hero.webp', '/assets/sector/brand-hero.svg'],
  ['/assets/sector/mascot-emotions.webp', '/assets/sector/mascot-emotions.svg'],
  ['/assets/sector/rank-badges.webp', '/assets/sector/rank-badges.svg'],
])

function sectorAssetAliases() {
  return {
    name: 'sector-stable-asset-aliases',
    enforce: 'pre',
    transform(code, id) {
      if (!/\.(?:js|jsx|ts|tsx)$/.test(id)) return null
      let next = code
      for (const [legacyPath, stablePath] of SECTOR_ASSET_ALIASES) {
        next = next.split(legacyPath).join(stablePath)
      }
      if (id.endsWith('/src/App.jsx')) {
        next = next.split("./pages/SectorPetPage").join("./pages/SectorPetPersianPage")
      }
      return next === code ? null : { code: next, map: null }
    },
  }
}

export default defineConfig({
  plugins: [sectorAssetAliases(), react()],
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_BASE_URL || 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          react: ['react', 'react-dom'],
        }
      }
    }
  }
})
