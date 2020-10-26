import { Pages, Role, SessionStorageKeys } from '@/util/constants'
import AcceptInviteLandingView from '@/views/auth/AcceptInviteLandingView.vue'
import AcceptInviteView from '@/views/auth/AcceptInviteView.vue'
import AccountChangeSuccessView from '@/views/auth/create-account/AccountChangeSuccessView.vue'
import AccountChangeView from '@/views/auth/create-account/AccountChangeView.vue'
import AccountCreationSuccessView from '@/views/auth/create-account/AccountCreationSuccessView.vue'
import AccountInstructions from '@/components/auth/create-account/non-bcsc/AccountInstructions.vue'
import AccountLoginOptionsChooser from '@/views/auth/AccountLoginOptionsChooser.vue'
import AccountLoginOptionsInfo from '@/views/auth/AccountLoginOptionsInfo.vue'
import AccountSetupView from '@/views/auth/create-account/AccountSetupView.vue'
import AffidavitDownload from '@/components/auth/create-account/non-bcsc/AffidavitDownload.vue'
import AuthenticationOptionsView from '@/views/auth/AuthenticationOptionsView.vue'
import BusinessProfileView from '@/views/auth/BusinessProfileView.vue'
import ChooseAuthMethodView from '@/views/auth/ChooseAuthMethodView.vue'
import ConfigHelper from '@/util/config-helper'
import CreateAccountView from '@/views/auth/CreateAccountView.vue'
import DashboardView from '@/views/auth/DashboardView.vue'
import DecideBusinessView from '@/views/auth/home/DecideBusinessView.vue'
import DuplicateTeamWarningView from '@/views/auth/DuplicateTeamWarningView.vue'
import EntityManagement from '@/components/auth/manage-business/EntityManagement.vue'
import GLCodesListView from '@/views/auth/staff/GLCodesListView.vue'
import HomeView from '@/views/auth/home/HomeView.vue'
import IncorpOrRegisterView from '@/views/auth/home/IncorpOrRegisterView.vue'
import LeaveTeamLandingView from '@/views/auth/LeaveTeamLandingView.vue'
import MaintainBusinessView from '@/views/auth/home/MaintainBusinessView.vue'
import NonBcscAccountCreationSuccessView from '@/views/auth/create-account/non-bcsc/NonBcscAccountCreationSuccessView.vue'
import NonBcscAccountSetupView from '@/views/auth/create-account/non-bcsc/NonBcscAccountSetupView.vue'
import NonBcscInfoView from '@/views/auth/create-account/non-bcsc/NonBcscInfoView.vue'
import PageNotFound from '@/views/auth/PageNotFound.vue'
import PaymentReturnView from '@/views/pay/PaymentReturnView.vue'
import PaymentView from '@/views/pay/PaymentView.vue'
import PendingApprovalView from '@/views/auth/PendingApprovalView.vue'
import ProfileDeactivatedView from '@/views/auth/ProfileDeactivatedView.vue'
import RequestNameView from '@/views/auth/home/RequestNameView.vue'
import ReviewAccountView from '@/views/auth/staff/ReviewAccountView.vue'
import { RouteConfig } from 'vue-router'
import SetupAccountSuccessView from '@/views/auth/staff/SetupAccountSuccessView.vue'
import SetupAccountView from '@/views/auth/staff/SetupAccountView.vue'
import SigninView from '@/views/auth/SigninView.vue'
import SignoutView from '@/views/auth/SignoutView.vue'
import StaffActiveAccountsTable from '@/components/auth/staff/account-management/StaffActiveAccountsTable.vue'
import StaffDashboardView from '@/views/auth/staff/StaffDashboardView.vue'
import StaffPendingAccountInvitationsTable from '@/components/auth/staff/account-management/StaffPendingAccountInvitationsTable.vue'
import StaffPendingAccountsTable from '@/components/auth/staff/account-management/StaffPendingAccountsTable.vue'
import StaffRejectedAccountsTable from '@/components/auth/staff/account-management/StaffRejectedAccountsTable.vue'
import TermsOfServiceDeclineView from '@/views/auth/TermsOfServiceDeclineView.vue'
import TermsOfServiceView from '@/views/auth/TermsOfServiceView.vue'
import UnauthorizedView from '@/views/auth/UnauthorizedView.vue'
import UserProfileView from '@/views/auth/UserProfileView.vue'

function mapReturnPayVars (route: any) {
  let payResponseUrl = window.location.search
  if (payResponseUrl && payResponseUrl.charAt(0) === '?') {
    payResponseUrl = payResponseUrl.substr(1)
  }
  return {
    paymentId: route.params.paymentId,
    transactionId: route.params.transactionId,
    payResponseUrl: payResponseUrl
  }
}

export function getRoutes (): RouteConfig[] {
  const accountSettings = () => import(/* webpackChunkName: "account-settings" */ '../views/auth/AccountSettings.vue')
  const accountInfo = () => import(/* webpackChunkName: "account-settings" */ '../components/auth/account-settings/account-info/AccountInfo.vue')
  const teamManagement = () => import(/* webpackChunkName: "account-settings" */ '../components/auth/account-settings/team-management/TeamManagement.vue')
  const accountLoginOption = () => import(/* webpackChunkName: "account-settings" */ '../components/auth/account-settings/login-options/AccountSettingsLoginOption.vue')
  const accountPaymentOption = () => import(/* webpackChunkName: "account-settings" */ '../components/auth/account-settings/payment/AccountPaymentMethods.vue')
  const transaction = () => import(/* webpackChunkName: "account-settings" */ '../components/auth/account-settings/transaction/Transactions.vue')
  const statements = () => import(/* webpackChunkName: "account-settings" */ '../components/auth/account-settings/statement/Statements.vue')
  const routes = [
    { path: '/', name: 'root', redirect: 'home' },
    {
      path: '/home',
      name: 'home',
      component: HomeView,
      children: [
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
      ],
      meta: { showNavBar: false }
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
            disabledRoles: [Role.AnonymousUser],
            requiresActiveAccount: true
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
          path: 'login-option',
          name: 'login-option',
          component: accountLoginOption
        },
        {
          path: 'payment-option',
          name: 'payment-option',
          component: accountPaymentOption
        },
        {
          path: 'transactions',
          name: 'transactions',
          component: transaction,
          meta: {
            isPremiumOnly: true
          }
        },
        {
          path: 'statements',
          name: 'statements',
          component: statements,
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
      path: '/setup-non-bcsc-account',
      name: 'setup-non-bcsc-account',
      component: NonBcscAccountSetupView,
      props: true,
      meta: { requiresAuth: true, requiresProfile: true }
    },
    {
      path: '/nonbcsc-info',
      name: 'nonbcsc-info',
      component: NonBcscInfoView,
      props: true,
      redirect: '/nonbcsc-info/instructions',
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
      meta: { requiresAuth: true, allowedRoles: [Role.StaffManageAccounts] },
      props: true
    },
    {
      path: '/setup-non-bcsc-account-success',
      name: 'setup-non-bcsc-account-success',
      component: NonBcscAccountCreationSuccessView,
      meta: { requiresAuth: true, requiresProfile: true }
    },
    {
      path: '/userprofile/:token?',
      name: 'userprofile',
      component: UserProfileView,
      props: true,
      meta: { requiresAuth: true, requiresProfile: true }
    },
    {
      path: '/choose-authentication-method',
      name: 'chooseauthmethodview',
      component: ChooseAuthMethodView,
      meta: { requiresAuth: false, requiresProfile: false },
      props: true
    },
    {
      path: '/account-login-options-chooser',
      component: AccountLoginOptionsChooser,
      meta: { requiresAuth: true, requiresProfile: true },
      props: true
    },
    {
      path: '/account-login-options-info',
      component: AccountLoginOptionsInfo,
      meta: { requiresAuth: true, requiresProfile: true },
      props: true
    },
    {
      path: '/authentication-options',
      component: AuthenticationOptionsView,
      meta: { requiresAuth: false },
      props: true
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
      // to handle old invitation; removable this after a month of this release
      redirect: '/undefined/validatetoken/BCSC/:token'
    },
    {
      path: '/confirmtoken/:token',
      name: 'confirmtoken',
      component: AcceptInviteView,
      props: true,
      meta: { requiresAuth: true, disabledRoles: [Role.Staff] }
    },
    {
      // to handle old invitation; removable this after a month of this release
      path: '/:orgName/dirsearch/validatetoken/:token',
      name: 'createuserprofile',
      redirect: '/:orgName/validatetoken/BCROS/:token'
    },
    {
      path: '/:orgName/validatetoken/:loginSource/:token',
      component: AcceptInviteLandingView,
      props: true,
      meta: { requiresAuth: false }
    },
    { path: '/signin/:idpHint',
      name: 'signin',
      component: SigninView,
      props: true,
      meta: { requiresAuth: false } },
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
      path: Pages.STAFF_DASHBOARD,
      name: 'staff-dashboard',
      component: StaffDashboardView,
      props: true,
      meta: { requiresAuth: true, allowedRoles: [Role.Staff] },
      children: [
        {
          path: '',
          redirect: 'active'
        },
        {
          path: 'active',
          component: StaffActiveAccountsTable,
          name: 'active'
        },
        {
          path: 'invitations',
          component: StaffPendingAccountInvitationsTable,
          name: 'invitations'
        },
        {
          path: 'review',
          component: StaffPendingAccountsTable,
          name: 'review'
        },
        {
          path: 'rejected',
          component: StaffRejectedAccountsTable,
          name: 'rejected'
        }
      ]
    },
    {
      path: Pages.STAFF,
      name: 'staff',
      redirect: Pages.STAFF_DASHBOARD
    },
    {
      path: Pages.STAFF_DASHBOARD_OLD,
      name: 'searchbusiness',
      redirect: Pages.STAFF_DASHBOARD
    },
    {
      path: '/glcodelist',
      name: 'glcodelist',
      component: GLCodesListView,
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
      path: '/pendingapproval/:teamName?/:pendingAffidavit?',
      name: 'pendingapproval',
      component: PendingApprovalView,
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
