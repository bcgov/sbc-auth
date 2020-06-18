import { Role, SessionStorageKeys } from '@/util/constants'
import AcceptInviteLandingView from '@/views/auth/AcceptInviteLandingView.vue'
import AcceptInviteView from '@/views/auth/AcceptInviteView.vue'
import AccountChangeSuccessView from '@/views/auth/AccountChangeSuccessView.vue'
import AccountChangeView from '@/views/auth/AccountChangeView.vue'
import AccountCreationSuccessView from '@/views/auth/AccountCreationSuccessView.vue'
import AccountInstructions from '@/components/auth/ExtraProv/AccountInstructions.vue'
import AccountSetupView from '@/views/auth/AccountSetupView.vue'
import AffidavitDownload from '@/components/auth/ExtraProv/AffidavitDownload.vue'
import BusinessProfileView from '@/views/auth/BusinessProfileView.vue'
import ConfigHelper from '@/util/config-helper'
import CreateAccountView from '@/views/auth/CreateAccountView.vue'
import DashboardView from '@/views/auth/DashboardView.vue'
import DecideBusinessView from '@/views/auth/DecideBusinessView.vue'
import DuplicateTeamWarningView from '@/views/auth/DuplicateTeamWarningView.vue'
import EntityManagement from '@/components/auth/EntityManagement.vue'
import ExtraProvInfoView from '@/views/auth/OutOfProvinceAccountView.vue'
import ExtraProvincialAccountSetupView from '@/views/auth/ExtraProvincialAccountSetupView.vue'
import Home from '@/views/auth/Home.vue'
import IncorpOrRegisterView from '@/views/auth/IncorpOrRegisterView.vue'
import LeaveTeamLandingView from '@/views/auth/LeaveTeamLandingView.vue'
import MaintainBusinessView from '@/views/auth/MaintainBusinessView.vue'
import PageNotFound from '@/views/auth/PageNotFound.vue'
import PaymentReturnView from '@/views/pay/PaymentReturnView.vue'
import PaymentView from '@/views/pay/PaymentView.vue'
import PendingAffidavitApprovalView from '@/views/auth/PendingAffidavitApprovalView.vue'
import PendingApprovalView from '@/views/auth/PendingApprovalView.vue'
import ProfileDeactivatedView from '@/views/auth/ProfileDeactivatedView.vue'
import RequestNameView from '@/views/auth/RequestNameView.vue'
import ReviewAccountView from '@/views/auth/staff/ReviewAccountView.vue'
import { RouteConfig } from 'vue-router'
import SearchBusinessView from '@/views/auth/staff/SearchBusinessView.vue'
import SetupAccountSuccessView from '@/views/auth/staff/SetupAccountSuccessView.vue'
import SetupAccountView from '@/views/auth/staff/SetupAccountView.vue'
import SigninView from '@/views/auth/SigninView.vue'
import SignoutView from '@/views/auth/SignoutView.vue'
import TermsOfServiceDeclineView from '@/views/auth/TermsOfServiceDeclineView.vue'
import TermsOfServiceView from '@/views/auth/TermsOfServiceView.vue'
import UnauthorizedView from '@/views/auth/UnauthorizedView.vue'
import UserProfileView from '@/views/auth/UserProfileView.vue'

function mapReturnPayVars (route: any) {
  return {
    paymentId: route.params.paymentId,
    transactionId: route.params.transactionId,
    receiptNum: !route.query.receipt_number ? '' : route.query.receipt_number
  }
}

export function getRoutes (): RouteConfig[] {
  const accountSettings = () => import(/* webpackChunkName: "account-settings" */ '../views/auth/AccountSettings.vue')
  const accountInfo = () => import(/* webpackChunkName: "account-settings" */ '../components/auth/AccountInfo.vue')
  const teamManagement = () => import(/* webpackChunkName: "account-settings" */ '../components/auth/TeamManagement.vue')
  const transaction = () => import(/* webpackChunkName: "account-settings" */ '../components/auth/Transactions.vue')
  const routes = [
    { path: '/', name: 'root', redirect: 'home' },
    {
      path: '/home',
      name: 'home',
      component: Home,
      children: getEnvChildRoutes(),
      meta: { showNavBar: !ConfigHelper.getLaunchFeatureFlag() }
    },
    {
      path: '/business',
      name: 'business-root',
      meta: { requiresAuth: true, showNavBar: true },
      redirect: `/account/${JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.CurrentAccount) || '{}').id || 0}/business`
    },
    {
      path: '/account/:orgId',
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
    {
      path: '/account/:orgId/settings',
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
          component: transaction,
          meta: {
            isPremiumOnly: true
          }
        }
      ]
    },
    {
      path: '/change-account',
      name: 'changeaccount',
      component: AccountChangeView,
      props: true,
      meta: { requiresAuth: true, requiresProfile: true }
    },
    {
      path: '/setup-account',
      name: 'setupaccount',
      component: AccountSetupView,
      props: true,
      meta: { requiresAuth: true, requiresProfile: true }
    },
    {
      path: '/setup-extra-prov-account',
      name: 'setup-extra-prov-account',
      component: ExtraProvincialAccountSetupView,
      props: true,
      meta: { requiresAuth: true, requiresProfile: true }
    },
    {
      path: '/extraprov-info',
      name: 'extraprov-info',
      component: ExtraProvInfoView,
      props: true,
      redirect: '/extraprov-info/instructions',
      meta: { requiresAuth: false, requiresProfile: false },
      children: [
        {
          path: 'instructions',
          name: 'instructions',
          component: AccountInstructions
        },
        {
          path: 'download',
          name: 'download',
          component: AffidavitDownload
        }
      ]
    },
    {
      path: '/change-account-success',
      name: 'change-account-success',
      component: AccountChangeSuccessView,
      meta: { requiresAuth: true, requiresProfile: true }
    },
    {
      path: '/setup-account-success',
      name: 'setup-account-success',
      component: AccountCreationSuccessView,
      meta: { requiresAuth: true, requiresProfile: true }
    },
    {
      path: '/review-account/:orgId',
      name: 'review-account',
      component: ReviewAccountView,
      meta: { requiresAuth: true, disabledRoles: [Role.Basic, Role.Public] },
      props: true
    },
    {
      path: '/userprofile/:token?',
      name: 'userprofile',
      component: UserProfileView,
      props: true,
      meta: { requiresAuth: true, requiresProfile: true }
    },
    {
      path: '/createaccount',
      name: 'createaccount',
      component: CreateAccountView,
      meta: { requiresAuth: false, requiresProfile: false },
      props: true
    },
    {
      path: '/duplicateteam',
      name: 'duplicateteam',
      component: DuplicateTeamWarningView,
      meta: { requiresAuth: true }
    },
    {
      path: '/validatetoken/:token',
      name: 'validatetoken',
      component: AcceptInviteLandingView,
      props: true,
      meta: { requiresAuth: false, disabledRoles: [Role.Staff] }
    },
    {
      path: '/confirmtoken/:token',
      name: 'confirmtoken',
      component: AcceptInviteView,
      props: true,
      meta: { requiresAuth: true, disabledRoles: [Role.Staff] }
    },
    {
      path: '/:orgName/dirsearch/validatetoken/:token',
      name: 'createuserprofile',
      component: AcceptInviteLandingView,
      props: true,
      meta: { requiresAuth: false }
    },
    {
      path: '/dirsearch/confirmtoken/:token',
      name: 'dirsearch-confirmtoken',
      component: AcceptInviteView,
      props: true,
      meta: { requiresAuth: true }
    },
    { path: '/signin/:idpHint', name: 'signin', component: SigninView, props: true, meta: { requiresAuth: false } },
    {
      path: '/signin/:idpHint/:redirectUrl',
      name: 'signin-redirect',
      component: SigninView,
      props: true,
      meta: { requiresAuth: false }
    },
    {
      path: '/signin/:idpHint/:redirectUrl/:redirectUrlLoginFail',
      name: 'signin-redirect-full',
      component: SigninView,
      props: true,
      meta: { requiresAuth: false }
    },
    { path: '/signout', name: 'signout', component: SignoutView, props: true, meta: { requiresAuth: true } },
    {
      path: '/signout/:redirectUrl',
      name: 'signout-redirect',
      component: SignoutView,
      props: true,
      meta: { requiresAuth: true }
    },
    {
      path: '/businessprofile',
      name: 'businessprofile',
      component: BusinessProfileView,
      meta: { requiresAuth: true, requiresProfile: true, requiresActiveAccount: true, showNavBar: true }
    },
    {
      path: '/makepayment/:paymentId/:redirectUrl',
      name: 'makepayment',
      component: PaymentView,
      props: true,
      meta: { requiresAuth: false }
    },
    {
      path: '/profiledeactivated',
      name: 'profiledeactivated',
      component: ProfileDeactivatedView,
      props: true,
      meta: { requiresAuth: false }
    },
    {
      path: '/returnpayment/:paymentId/transaction/:transactionId',
      name: 'returnpayment',
      component: PaymentReturnView,
      props: mapReturnPayVars,
      meta: { requiresAuth: false }
    },
    {
      path: '/searchbusiness',
      name: 'searchbusiness',
      component: SearchBusinessView,
      props: true,
      meta: { requiresAuth: true, allowedRoles: [Role.Staff] }
    },
    {
      path: '/unauthorized',
      name: 'unauthorized',
      component: UnauthorizedView,
      props: true,
      meta: { requiresAuth: false }
    },
    {
      path: '/unauthorizedtermsdecline',
      name: 'unauthorizedtermsdecline',
      component: TermsOfServiceDeclineView,
      props: true,
      meta: { requiresAuth: true }
    },
    {
      path: '/pendingapproval/:team_name?',
      name: 'pendingapproval',
      component: PendingApprovalView,
      props: true,
      meta: { requiresAuth: true, requiresProfile: true }
    },
    {
      path: '/pendingaffidavitapproval/:team_name?',
      name: 'pendingaffidavitapproval',
      component: PendingAffidavitApprovalView,
      props: true,
      meta: { requiresAuth: true, requiresProfile: true }
    },
    {
      path: '/leaveteam',
      name: 'leaveteam',
      component: LeaveTeamLandingView,
      props: true,
      meta: { requiresAuth: true }
    },
    {
      path: '/staff-setup-account',
      name: 'staffsetupaccount',
      component: SetupAccountView,
      props: true,
      meta: { requiresAuth: true, allowedRoles: [Role.Staff] }
    },
    {
      path: '/staff-setup-account-success/:accountName?',
      name: 'staffsetupaccountsuccess',
      component: SetupAccountSuccessView,
      props: true,
      meta: { requiresAuth: true, allowedRoles: [Role.Staff] }
    },
    {
      path: '/userprofileterms/:token?',
      name: 'userprofileterms',
      props: true,
      component: TermsOfServiceView,
      meta: { requiresAuth: true }
    },
    { path: '*', name: 'notfound', component: PageNotFound }
  ]

  return routes
}

// Get the child routes depending on environment
const getEnvChildRoutes = () => {
  return ConfigHelper.getLaunchFeatureFlag() ? [
    {
      path: '',
      redirect: 'decide-business'
    },
    {
      path: 'decide-business',
      component: DecideBusinessView,
      meta: { showNavBar: false }
    },
    {
      path: 'request-name',
      component: RequestNameView,
      meta: { showNavBar: false }
    },
    {
      path: 'incorporate-or-register',
      component: IncorpOrRegisterView,
      meta: { showNavBar: false }
    },
    {
      path: 'maintain-business',
      component: MaintainBusinessView,
      meta: { showNavBar: false }
    }
  ]
    : []
}
