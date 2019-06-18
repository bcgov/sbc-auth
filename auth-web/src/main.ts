import Vue from 'vue'
import './plugins/vuetify'
import App from './App.vue'
import router from './router'
import store from './store'
import Axios from 'axios'
import i18n from './plugins/i18n'
// mutliple base urls now
// Axios.defaults.baseURL = process.env.VUE_APP_ROOT_API

// importing the helper
import interceptorsSetup from '@/util/interceptors'

Vue.config.productionTip = false

interceptorsSetup()

new Vue({
  router,
  store,
  i18n,
  render: (h) => h(App)
}).$mount('#app')
