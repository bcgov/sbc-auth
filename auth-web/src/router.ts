import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import AuthHome from './views/AuthHome.vue'
import BusinessProfile from './views/BusinessProfile.vue'
import Signin from './components/auth/Signin.vue'
import PaymentForm from './components/pay/PaymentForm.vue'
import PaymentReturnForm from './components/pay/PaymentReturnForm.vue'
import PageNotFound from './views/PageNotFound.vue'
import CreateAccount from './views/CreateAccount.vue'
import Template from './views/management/Template.vue'
import UserProfile from './views/UserProfile.vue'
import Dashboard from './components/auth/Dashboard.vue'
import Signout from './components/auth/Signout.vue'
import AddBusinessForm from './components/auth/AddBusinessForm.vue'
import configHelper from './util/config-helper'

Vue.use(Router)

function mapReturnPayVars (route) {
  return {
    paymentId: route.params.paymentId,
    transactionId: route.params.transactionId,
    receiptNum: !route.query.receipt_number ? '' : route.query.receipt_number
  }
}

export function getRoutes (appFlavor:String) {
  let varRoutes

  if (appFlavor === 'mvp') {
    varRoutes = [{ path: '/', component: Home }]
  } else {
    varRoutes = [
      { path: '/', component: Home },
      { path: '/home', component: AuthHome },
      { path: '/main', component: Template, meta: { requiresAuth: true } },
      { path: '/userprofile', component: UserProfile, props: true, meta: { requiresAuth: true } },
      { path: '/createaccount', component: CreateAccount, meta: { requiresAuth: false } }
    ]
  }

  let routes = [
    { path: '/signin/:idpHint', component: Signin, props: true, meta: { requiresAuth: false } },
    { path: '/signin/:idpHint/:redirectUrl', component: Signin, props: true, meta: { requiresAuth: false } },
    { path: '/signout', component: Signout, props: true, meta: { requiresAuth: true } },
    { path: '/signout/:redirectUrl', component: Signout, props: true, meta: { requiresAuth: true } },
    { path: '/businessprofile', component: BusinessProfile, meta: { requiresAuth: true } },
    { path: '/makepayment/:paymentId/:redirectUrl', component: PaymentForm, props: true, meta: { requiresAuth: true } },
    { path: '/returnpayment/:paymentId/transaction/:transactionId', component: PaymentReturnForm, props: mapReturnPayVars, meta: { requiresAuth: true } },
    { path: '*', component: PageNotFound }
  ]

  routes = [...varRoutes, ...routes]
  return routes
}

const router = new Router({
  mode: 'history',
  base: process.env.BASE_URL
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
