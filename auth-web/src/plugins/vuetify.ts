import 'material-icons/iconfont/material-icons.css' // Ensure you are using css-loader
import 'vuetify/dist/vuetify.min.css'
import '$assets/scss/base.scss'
import '$assets/scss/layout.scss'
import '$assets/scss/overrides.scss'

import Vue from 'vue'
import Vuetify from 'vuetify'

Vue.use(Vuetify)

export default new Vuetify({
  icons: {
    iconfont: 'md'
  }
})
