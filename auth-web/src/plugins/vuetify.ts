import 'vuetify/dist/vuetify.min.css'
import '$assets/scss/base.scss'
import '$assets/scss/layout.scss'
import '$assets/scss/overrides.scss'

import Vue from 'vue'
import Vuetify from 'vuetify'

Vue.use(Vuetify)

export default new Vuetify({
  theme: {
    themes: {
      light: {
        primary: '#003366',
        secondary: '#b0bec5',
        accent: '#8c9eff',
        error: '#b71c1c',
        info: '#2196F3',
        success: '#4CAF50',
        warning: '#fb8c00',
        anchor: '#1A5A96',
        grey: {
          base: '#adb5bd',
          lighten5: '#f8f9fa',
          lighten4: '#f1f3f5',
          lighten3: '#e9ecef',
          lighten2: '#dee2e6',
          lighten1: '#ced4da',
          darken1: '#868e96',
          darken2: '#495057',
          darken3: '#343a40',
          darken4: '#212529'
        },
        navBg: '#003366'
      }
    }
  }
})
