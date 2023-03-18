import { fileURLToPath } from 'node:url'
import { mergeConfig } from 'vite'
import { vi } from 'vitest'
import { configDefaults, defineConfig } from 'vitest/config'
import viteConfig from './vite.config'
import vuetify from 'vite-plugin-vuetify'
// import i18n from './src/i18n'

// vi.mock('./src/i18n');

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'jsdom',
      exclude: [...configDefaults.exclude, 'e2e/*'],
      root: fileURLToPath(new URL('./', import.meta.url))
    },
    plugins: [vuetify()],
    ssr: {
      noExternal: ['vuetify']
    }
  })
)
