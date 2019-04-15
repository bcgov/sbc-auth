import Vue from 'vue';
import './plugins/vuetify';
import App from './App.vue';
import router from './router';
import store from './store';
import Axios from 'axios';

Vue.config.productionTip = false;
Axios.defaults.baseURL = process.env.VUE_APP_ROOT_API;

new Vue({
  router,
  store,
  render: (h) => h(App)
}).$mount('#app');
