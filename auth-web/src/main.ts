import Vue from 'vue'
import './plugins/vuetify'
import App from './App.vue'
import router from './router'
import store from './store'
import Axios from 'axios'
import i18n from './plugins/i18n'

Vue.config.productionTip = false
// mutliple base urls now
// Axios.defaults.baseURL = process.env.VUE_APP_ROOT_API

new Vue({
  router,
  store,
  i18n,
  render: (h) => h(App)
}).$mount('#app')
