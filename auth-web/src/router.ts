import { Role, SessionStorageKeys } from '@/util/constants'
import AcceptInvite from '@/views/AcceptInvite.vue'
import AuthHome from '@/views/AuthHome.vue'
import BusinessProfile from '@/views/BusinessProfile.vue'
import CreateAccount from '@/views/CreateAccount.vue'
import EntityManagement from '@/views/management/EntityManagement.vue'
import Home from '@/views/Home.vue'
import KeyCloakService from '@/services/keycloak.services'
import PageNotFound from '@/views/PageNotFound.vue'
import PaymentForm from '@/components/pay/PaymentForm.vue'
import PaymentReturnForm from '@/components/pay/PaymentReturnForm.vue'
import Router from 'vue-router'
import SearchBusinessForm from '@/components/auth/SearchBusinessForm.vue'
import Signin from '@/components/auth/Signin.vue'
import Signout from '@/components/auth/Signout.vue'
import TokenValidator from '@/views/TokenValidator.vue'
import Unauthorized from '@/components/auth/Unauthorized.vue'
import UserManagement from '@/views/management/UserManagement.vue'
import UserProfile from '@/views/UserProfile.vue'
import Vue from 'vue'

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
      { path: '/', component: AuthHome },
      { path: '/home', component: AuthHome },
      { path: '/main', component: EntityManagement, meta: { requiresAuth: true } },
      { path: '/team', component: UserManagement, meta: { requiresAuth: true } },
      { path: '/userprofile', component: UserProfile, props: true, meta: { requiresAuth: true } },
      { path: '/createaccount', component: CreateAccount, meta: { requiresAuth: false } },
      { path: '/validatetoken/:token', component: TokenValidator, props: true, meta: { requiresAuth: false, disabledRoles: [Role.Staff] } },
      { path: '/confirmtoken/:token', component: AcceptInvite, props: true, meta: { requiresAuth: true, disabledRoles: [Role.Staff] } }
    ]
  }

  let routes = [
    { path: '/signin/:idpHint', component: Signin, props: true, meta: { requiresAuth: false } },
    { path: '/signin/:idpHint/:redirectUrl', component: Signin, props: true, meta: { requiresAuth: false } },
    { path: '/signout', component: Signout, props: true, meta: { requiresAuth: true } },
    { path: '/signout/:redirectUrl', component: Signout, props: true, meta: { requiresAuth: true } },
    { path: '/businessprofile', component: BusinessProfile, meta: { requiresAuth: true } },
    { path: '/makepayment/:paymentId/:redirectUrl', component: PaymentForm, props: true, meta: { requiresAuth: true, disabledRoles: [Role.Staff] } },
    { path: '/returnpayment/:paymentId/transaction/:transactionId', component: PaymentReturnForm, props: mapReturnPayVars, meta: { requiresAuth: true, disabledRoles: [Role.Staff] } },
    { path: '/searchbusiness', component: SearchBusinessForm, props: true, meta: { requiresAuth: true, allowedRoles: [Role.Staff] } },
    { path: '/unauthorized', component: Unauthorized, props: true, meta: { requiresAuth: false } },
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
  // If the user is authenticated;
  //    If there are allowed or disabled roles specified on the route check if the user has those roles else route to unauthorized
  // If the user is not authenticated
  //    Redirect the user to login page to login page
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (sessionStorage.getItem(SessionStorageKeys.KeyCloakToken)) {
      if (KeyCloakService.verifyRoles(to.meta.allowedRoles, to.meta.disabledRoles)) {
        return next()
      } else {
        return next({
          path: '/unauthorized',
          query: { redirect: to.fullPath }
        })
      }
    } else {
      return next({
        path: '/', // TODO Change this to login home page once it's ready
        query: { redirect: to.fullPath }
      })
    }
  }
  next()
})

export default router
