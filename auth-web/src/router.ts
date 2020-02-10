import { Role, SessionStorageKeys } from '@/util/constants'
import AcceptInviteLandingView from '@/views/auth/AcceptInviteLandingView.vue'
import AcceptInviteView from '@/views/auth/AcceptInviteView.vue'
import BusinessProfileView from '@/views/auth/BusinessProfileView.vue'
import CreateAccountView from '@/views/auth/CreateAccountView.vue'
import DashboardView from '@/views/auth/DashboardView.vue'
import DuplicateTeamWarningView from '@/views/auth/DuplicateTeamWarningView.vue'
import EntityManagement from '@/components/auth/EntityManagement.vue'
import HomeView from '@/views/auth/HomeView.vue'
import KeyCloakService from '@/services/keycloak.services'
import LeaveTeamLandingView from '@/views/auth/LeaveTeamLandingView.vue'
import PageNotFound from '@/views/auth/PageNotFound.vue'
import PaymentReturnView from '@/views/pay/PaymentReturnView.vue'
import PaymentView from '@/views/pay/PaymentView.vue'
import PendingApprovalView from '@/views/auth/PendingApprovalView.vue'
import ProfileDeactivatedView from '@/views/auth/ProfileDeactivatedView.vue'
import Router from 'vue-router'
import SearchBusinessView from '@/views/auth/SearchBusinessView.vue'
import SigninView from '@/views/auth/SigninView.vue'
import SignoutView from '@/views/auth/SignoutView.vue'
import UnauthorizedView from '@/views/auth/UnauthorizedView.vue'
import UserProfileView from '@/views/auth/UserProfileView.vue'

import Vue from 'vue'

Vue.use(Router)

function mapReturnPayVars (route: any) {
  return {
    paymentId: route.params.paymentId,
    transactionId: route.params.transactionId,
    receiptNum: !route.query.receipt_number ? '' : route.query.receipt_number
  }
}

export function getRoutes () {
  const accountSettings = () => import(/* webpackChunkName: "account-settings" */ './views/auth/AccountSettings.vue')
  const accountInfo = () => import(/* webpackChunkName: "account-settings" */ './components/auth/AccountInfo.vue')
  const userManagement = () => import(/* webpackChunkName: "account-settings" */ './components/auth/UserManagement.vue')
  const routes = [
    { path: '/', component: HomeView },
    { path: '/home', component: HomeView },
    { path: '/account/:orgId',
      component: DashboardView,
      meta: { requiresAuth: true },
      redirect: '/account/:orgId/business',
      props: true,
      children: [
        {
          path: 'business',
          component: EntityManagement,
          props: true
        }]
    },
    { path: '/account/:orgId/settings',
      component: accountSettings,
      meta: { requiresAuth: true },
      redirect: '/account/:orgId/settings/account-info',
      props: true,
      children: [
        {
          path: 'account-info',
          component: accountInfo
        },
        {
          path: 'team-members',
          component: userManagement
        }
      ]
    },
    { path: '/userprofile', component: UserProfileView, props: true, meta: { requiresAuth: true } },
    { path: '/createaccount', component: CreateAccountView, meta: { requiresAuth: true } },
    { path: '/duplicateteam', component: DuplicateTeamWarningView, meta: { requiresAuth: true } },
    { path: '/validatetoken/:token', component: AcceptInviteLandingView, props: true, meta: { requiresAuth: false, disabledRoles: [Role.Staff] } },
    { path: '/confirmtoken/:token', component: AcceptInviteView, props: true, meta: { requiresAuth: true, disabledRoles: [Role.Staff] } },
    { path: '/signin/:idpHint', component: SigninView, props: true, meta: { requiresAuth: false } },
    { path: '/signin/:idpHint/:redirectUrl', component: SigninView, props: true, meta: { requiresAuth: false } },
    { path: '/signout', component: SignoutView, props: true, meta: { requiresAuth: true } },
    { path: '/signout/:redirectUrl', component: SignoutView, props: true, meta: { requiresAuth: true } },
    { path: '/businessprofile', component: BusinessProfileView, meta: { requiresAuth: true } },
    { path: '/makepayment/:paymentId/:redirectUrl', component: PaymentView, props: true, meta: { requiresAuth: false } },
    { path: '/profiledeactivated', component: ProfileDeactivatedView, props: true, meta: { requiresAuth: false } },
    { path: '/returnpayment/:paymentId/transaction/:transactionId', component: PaymentReturnView, props: mapReturnPayVars, meta: { requiresAuth: false } },
    { path: '/searchbusiness', component: SearchBusinessView, props: true, meta: { requiresAuth: true, allowedRoles: [Role.Staff] } },
    { path: '/unauthorized', component: UnauthorizedView, props: true, meta: { requiresAuth: false } },
    { path: '/pendingapproval/:team_name?', component: PendingApprovalView, props: true, meta: { requiresAuth: false } },
    { path: '/leaveteam', component: LeaveTeamLandingView, props: true, meta: { requiresAuth: true } },
    { path: '*', component: PageNotFound }
  ]

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
      let nextPath
      if (to.meta.allowedRoles.length === 1 && to.meta.allowedRoles[0] === Role.Staff) {
        nextPath = {
          path: '/signin/idir' + to.path
        }
      } else {
        nextPath = {
          path: '/',
          query: { redirect: to.fullPath }
        }
      }
      return next(nextPath)
    }
  }
  next()
})

export default router
