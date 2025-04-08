import EnvironmentPlugin from 'vite-plugin-environment'
import { defineConfig } from 'vite'
import fs from 'fs'
import path from 'path'
import pluginRewriteAll from 'vite-plugin-rewrite-all'
import postcssNesting from 'postcss-nesting'
import { createVuePlugin as vue } from 'vite-plugin-vue2'

const packageJson = fs.readFileSync('./package.json') as unknown as string
const appName = JSON.parse(packageJson).appName
const appVersion = JSON.parse(packageJson).version
const sbcName = JSON.parse(packageJson).sbcName
const sbcVersion = JSON.parse(packageJson).dependencies['sbc-common-components']
const aboutText1 = (appName && appVersion) ? `${appName} v${appVersion}` : ''
const aboutText2 = (sbcName && sbcVersion) ? `${sbcName} v${sbcVersion}` : ''
const generateAboutText = (aboutText1, aboutText2) => {
  if (aboutText1 && aboutText2) {
    return `"${aboutText1}<br>${aboutText2}"`
  } else if (aboutText1) {
    return `"${aboutText1}"`
  } else if (aboutText2) {
    return `"${aboutText2}"`
  } else {
    return ''
  }
}

export default defineConfig({
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "./src/assets/scss/theme.scss";`
      }
    }
  },
  define: {
    'import.meta.env.ABOUT_TEXT': generateAboutText(aboutText1, aboutText2),
    'import.meta.env.APP_NAME': JSON.stringify(appName)
  },
  esbuild: {
    minifySyntax: false,
    minifyIdentifiers: false
  },
  envPrefix: 'VUE_APP_', // Need to remove this after fixing vaults. Use import.meta.env with VUE_APP.
  plugins: [
    vue({
      vueTemplateOptions: {
        transformAssetUrls: {
          img: ['src', 'data-src'],
          'v-app-bar': ['image'],
          'v-avatar': ['image'],
          'v-banner': ['avatar'],
          'v-card': ['image'],
          'v-card-item': ['prependAvatar', 'appendAvatar'],
          'v-chip': ['prependAvatar', 'appendAvatar'],
          'v-img': ['src', 'lazySrc', 'srcset'],
          'v-list-item': ['prependAvatar', 'appendAvatar'],
          'v-navigation-bar': ['image'],
          'v-parallax': ['src', 'lazySrc', 'srcset'],
          'v-toolbar': ['image']
        }
      }
    }),
    EnvironmentPlugin({
      BUILD: 'web' // Fix for Vuelidate, allows process.env with Vite.
    }),
    postcssNesting,
    pluginRewriteAll()
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '~': path.resolve(__dirname, './node_modules'),
      '$assets': path.resolve(__dirname, './src/assets'),
      // Fix for bcrs-shared-components unit tests fail
      '@bcrs-shared-components/mixins': path.resolve(__dirname, './node_modules/@bcrs-shared-components/mixins/index.ts'),
      '@bcrs-shared-components/enums': path.resolve(__dirname, './node_modules/@bcrs-shared-components/enums/index.ts')
    },
    extensions: ['.js', '.ts', '.vue', '.json', '.css']
  },
  server: {
    port: 8080,
    host: true
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/unit/setup.ts',
    threads: true,
    // hide Vue Devtools message
    onConsoleLog: function (log) {
      if (log.includes('Download the Vue Devtools extension')) {
        return false
      }
    },
    deps: {
      // Need sbc-common-components in there otherwise vue error
      inline: ['vuetify', 'sbc-common-components']
    }
  },
  // Needs to be in here so there aren't two instances of sbc-common-components created.
  optimizeDeps: {
    exclude: ['@vue/composition-api', 'sbc-common-components']
  }
})
