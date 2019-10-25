import 'material-icons/iconfont/material-icons.css' // Ensure you are using css-loader
import Vue from 'vue'
import Vuetify from 'vuetify'

Vue.use(Vuetify)

export default new Vuetify({
  icons: {
    iconfont: 'md'
  }
})
