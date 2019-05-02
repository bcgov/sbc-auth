import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import PageNotFound from './views/PageNotFound.vue'

Vue.use(Router)

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      // just handle it better when its getting deployed to prod
      path: '*',
      name: 'PageNotFound',
      component: PageNotFound
    }
  ]
})
