import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import BusinessProfile from './views/BusinessProfile.vue'
import PaymentForm from './components/pay/PaymentForm.vue'
import PaymentReturnForm from './components/pay/PaymentReturnForm.vue'
import PageNotFound from './views/PageNotFound.vue'

Vue.use(Router)

function mapReturnPayVars (route) {
  return {
    paymentId: route.params.paymentId,
    transactionId: route.params.transactionId,
    receiptNum: !route.query.receipt_number ? '' : route.query.receipt_number
  }
}

const routes = [
  { path: '/', component: Home },
  { path: '/businessprofile', component: BusinessProfile, meta: { requiresAuth: true } },
  { path: '/makepayment/:paymentId/:redirectUrl', component: PaymentForm, props: true, meta: { requiresAuth: true } },
  { path: '/returnpayment/:paymentId/transaction/:transactionId', component: PaymentReturnForm, props: mapReturnPayVars, meta: { requiresAuth: true } },
  { path: '*', component: PageNotFound }
]

const router = new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (sessionStorage.getItem('KEYCLOAK_TOKEN')) {
      next()
    } else {
      next({
        path: '/',
        query: { redirect: to.fullPath }
      })
    }
  } else {
    next()
  }
})

export default router
