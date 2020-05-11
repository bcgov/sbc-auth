import { LoginSource, Pages, Role, SessionStorageKeys } from '@/util/constants'
import { Member, MembershipStatus, Organization } from '@/models/Organization'
import Router, { Route, RouteConfig } from 'vue-router'
import AcceptInviteLandingView from '@/views/auth/AcceptInviteLandingView.vue'
import AcceptInviteView from '@/views/auth/AcceptInviteView.vue'
import AccountChangeSuccessView from '@/views/auth/AccountChangeSuccessView.vue'
import AccountChangeView from '@/views/auth/AccountChangeView.vue'
import AccountCreationSuccessView from '@/views/auth/AccountCreationSuccessView.vue'
import { AccountSettings } from '@/models/account-settings'
import AccountSetupView from '@/views/auth/AccountSetupView.vue'
import BusinessProfileView from '@/views/auth/BusinessProfileView.vue'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import CreateAccountView from '@/views/auth/CreateAccountView.vue'
import DashboardView from '@/views/auth/DashboardView.vue'
import DuplicateTeamWarningView from '@/views/auth/DuplicateTeamWarningView.vue'
import EntityManagement from '@/components/auth/EntityManagement.vue'
import HomeView from '@/views/auth/HomeView.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import KeyCloakService from 'sbc-common-components/src/services/keycloak.services'
import LeaveTeamLandingView from '@/views/auth/LeaveTeamLandingView.vue'
import PageNotFound from '@/views/auth/PageNotFound.vue'
import PaymentReturnView from '@/views/pay/PaymentReturnView.vue'
import PaymentView from '@/views/pay/PaymentView.vue'
import PendingApprovalView from '@/views/auth/PendingApprovalView.vue'
import ProfileDeactivatedView from '@/views/auth/ProfileDeactivatedView.vue'
import SearchBusinessView from '@/views/auth/staff/SearchBusinessView.vue'
import SetupAccountSuccessView from '@/views/auth/staff/SetupAccountSuccessView.vue'
import SetupAccountView from '@/views/auth/staff/SetupAccountView.vue'
import SigninView from '@/views/auth/SigninView.vue'
import SignoutView from '@/views/auth/SignoutView.vue'
import TermsOfServiceDeclineView from '@/views/auth/TermsOfServiceDeclineView.vue'
import TermsOfServiceView from '@/views/auth/TermsOfServiceView.vue'
import UnauthorizedView from '@/views/auth/UnauthorizedView.vue'
import { User } from '@/models/user'
import UserProfileView from '@/views/auth/UserProfileView.vue'
import Vue from 'vue'
import store from '@/store'

Vue.use(Router)

function mapReturnPayVars (route: any) {
  return {
    paymentId: route.params.paymentId,
    transactionId: route.params.transactionId,
    receiptNum: !route.query.receipt_number ? '' : route.query.receipt_number
  }
}

export function getRoutes (): RouteConfig[] {
  const accountSettings = () => import(/* webpackChunkName: "account-settings" */ './views/auth/AccountSettings.vue')
  const accountInfo = () => import(/* webpackChunkName: "account-settings" */ './components/auth/AccountInfo.vue')
  const teamManagement = () => import(/* webpackChunkName: "account-settings" */ './components/auth/TeamManagement.vue')
  const transaction = () => import(/* webpackChunkName: "account-settings" */ './components/auth/Transactions.vue')
  const routes = [
    { path: '/', name: 'root', component: HomeView, meta: { showNavBar: true } },
    { path: '/home', name: 'home', component: HomeView, meta: { showNavBar: true } },
    { path: '/business',
      name: 'business-root',
      meta: { requiresAuth: true, showNavBar: true },
      redirect: `/account/${JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.CurrentAccount) || '{}').id || 0}/business`
    },
    { path: '/account/:orgId',
      name: 'account',
      component: DashboardView,
      meta: { requiresAuth: true, requiresProfile: true },
      redirect: '/account/:orgId/business',
      props: true,
      children: [
        {
          path: 'business',
          name: 'business',
          component: EntityManagement,
          props: true,
          meta: {
            showNavBar: true,
            disabledRoles: [Role.AnonymousUser]
          }
        }]
    },
    { path: '/account/:orgId/settings',
      name: 'account-settings',
      component: accountSettings,
      meta: { requiresAuth: true, requiresProfile: true, requiresActiveAccount: true },
      redirect: '/account/:orgId/settings/account-info',
      props: true,
      children: [
        {
          path: 'account-info',
          name: 'account-info',
          component: accountInfo
        },
        {
          path: 'team-members',
          name: 'team-members',
          component: teamManagement
        },
        {
          path: 'transactions',
          name: 'transactions',
          component: transaction
        }
      ]
    },
    { path: '/change-account', name: 'changeaccount', component: AccountChangeView, props: true, meta: { requiresAuth: true, requiresProfile: true } },
    { path: '/setup-account', name: 'setupaccount', component: AccountSetupView, props: true, meta: { requiresAuth: true, requiresProfile: true } },
    { path: '/change-account-success', name: 'change-account-success', component: AccountChangeSuccessView, meta: { requiresAuth: true, requiresProfile: true } },
    { path: '/setup-account-success', name: 'setup-account-success', component: AccountCreationSuccessView, meta: { requiresAuth: true, requiresProfile: true } },
    { path: '/userprofile/:token?', name: 'userprofile', component: UserProfileView, props: true, meta: { requiresAuth: true, requiresProfile: true } },
    { path: '/createaccount', name: 'createaccount', component: CreateAccountView, meta: { requiresAuth: false, requiresProfile: false }, props: true },
    { path: '/duplicateteam', name: 'duplicateteam', component: DuplicateTeamWarningView, meta: { requiresAuth: true } },
    { path: '/validatetoken/:token', name: 'validatetoken', component: AcceptInviteLandingView, props: true, meta: { requiresAuth: false, disabledRoles: [Role.Staff] } },
    { path: '/confirmtoken/:token', name: 'confirmtoken', component: AcceptInviteView, props: true, meta: { requiresAuth: true, disabledRoles: [Role.Staff] } },
    { path: '/:orgName/dirsearch/validatetoken/:token', name: 'createuserprofile', component: AcceptInviteLandingView, props: true, meta: { requiresAuth: false } },
    { path: '/dirsearch/confirmtoken/:token', name: 'dirsearch-confirmtoken', component: AcceptInviteView, props: true, meta: { requiresAuth: true } },
    { path: '/signin/:idpHint', name: 'signin', component: SigninView, props: true, meta: { requiresAuth: false } },
    { path: '/signin/:idpHint/:redirectUrl', name: 'signin-redirect', component: SigninView, props: true, meta: { requiresAuth: false } },
    { path: '/signin/:idpHint/:redirectUrl/:redirectUrlLoginFail', name: 'signin-redirect-full', component: SigninView, props: true, meta: { requiresAuth: false } },
    { path: '/signout', name: 'signout', component: SignoutView, props: true, meta: { requiresAuth: true } },
    { path: '/signout/:redirectUrl', name: 'signout-redirect', component: SignoutView, props: true, meta: { requiresAuth: true } },
    { path: '/businessprofile', name: 'businessprofile', component: BusinessProfileView, meta: { requiresAuth: true, requiresProfile: true, requiresActiveAccount: true, showNavBar: true } },
    { path: '/makepayment/:paymentId/:redirectUrl', name: 'makepayment', component: PaymentView, props: true, meta: { requiresAuth: false } },
    { path: '/profiledeactivated', name: 'profiledeactivated', component: ProfileDeactivatedView, props: true, meta: { requiresAuth: false } },
    { path: '/returnpayment/:paymentId/transaction/:transactionId', name: 'returnpayment', component: PaymentReturnView, props: mapReturnPayVars, meta: { requiresAuth: false } },
    { path: '/searchbusiness', name: 'searchbusiness', component: SearchBusinessView, props: true, meta: { requiresAuth: true, allowedRoles: [Role.Staff] } },
    { path: '/unauthorized', name: 'unauthorized', component: UnauthorizedView, props: true, meta: { requiresAuth: false } },
    { path: '/unauthorizedtermsdecline', name: 'unauthorizedtermsdecline', component: TermsOfServiceDeclineView, props: true, meta: { requiresAuth: true } },
    { path: '/pendingapproval/:team_name?', name: 'pendingapproval', component: PendingApprovalView, props: true, meta: { requiresAuth: true, requiresProfile: true } },
    { path: '/leaveteam', name: 'leaveteam', component: LeaveTeamLandingView, props: true, meta: { requiresAuth: true } },
    { path: '/staff-setup-account', name: 'staffsetupaccount', component: SetupAccountView, props: true, meta: { requiresAuth: true, allowedRoles: [Role.Staff] } },
    { path: '/staff-setup-account-success/:accountName?', name: 'staffsetupaccountsuccess', component: SetupAccountSuccessView, props: true, meta: { requiresAuth: true, allowedRoles: [Role.Staff] } },
    { path: '/userprofileterms/:token?', name: 'userprofileterms', props: true, component: TermsOfServiceView, meta: { requiresAuth: true } },
    { path: '*', name: 'notfound', component: PageNotFound }
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
      if (!KeyCloakService.verifyRoles(to.meta.allowedRoles, to.meta.disabledRoles)) {
        return next({
          path: '/unauthorized',
          query: { redirect: to.fullPath }
        })
      }
    } else {
      if (to.meta.allowedRoles?.length === 1 && to.meta.allowedRoles[0] === Role.Staff) {
        return next({
          path: `/signin/idir${to.path}`,
          query: { redirect: to.fullPath }
        })
      }
      return next({
        path: '/unauthorized',
        query: { redirect: to.fullPath }
      })
    }
  }

  // Enforce navigation guards are checked before navigating anywhere else
  // If store is not ready, we place a watch on it, then proceed when ready
  if (store.getters.loading) {
    store.watch(
      (state, getters) => getters.loading,
      value => {
        if (value === false) {
          proceed(to)
        }
      })
  } else {
    proceed()
  }

  function proceed (originalTarget?: Route) {
    const userContact: Contact = (store.state as any)?.user?.userContact
    const userProfile: User = (store.state as any)?.user?.userProfile
    const currentAccountSettings: AccountSettings = (store.state as any)?.org.currentAccountSettings
    const currentOrganization: Organization = (store.state as any)?.org?.currentOrganization
    const currentMembership: Member = (store.state as any)?.org?.currentMembership
    const currentUser: KCUserProfile = (store.state as any)?.user?.currentUser
    if (to.matched.some(record => record.meta.requiresProfile) &&
      !userProfile?.userTerms?.isTermsOfUseAccepted) {
      switch (currentUser?.loginSource) {
        case LoginSource.BCSC:
          return next({
            path: `/${Pages.USER_PROFILE_TERMS}`
          })
        case LoginSource.BCROS:
          return next({
            path: `/${Pages.USER_PROFILE_TERMS}`
          })
        default:
          return next({
            path: '/'
          })
      }
    }

    if (to.matched.some(record => record.meta.requiresActiveAccount) && currentUser.loginSource === LoginSource.BCSC) {
      if (currentAccountSettings && currentMembership.membershipStatus === MembershipStatus.Pending) {
        return next({ path: `/${Pages.PENDING_APPROVAL}/${currentAccountSettings?.label}` })
      } else if (!currentOrganization || currentMembership.membershipStatus !== MembershipStatus.Active) {
        return next({ path: `/${Pages.CREATE_ACCOUNT}` })
      }
    }
    originalTarget ? next(originalTarget) : next()
  }
})

export default router
