import {
  MyBusinessRegistryBreadcrumb,
  RegistryDashboardBreadcrumb,
  RegistryHomeBreadcrumb,
  StaffBusinessRegistryBreadcrumb,
  StaffDashboardBreadcrumb
} from '@/resources/BreadcrumbResources'
import { Pages, Role, SessionStorageKeys } from '@/util/constants'

import AcceptInviteLandingView from '@/views/auth/AcceptInviteLandingView.vue'
import AcceptInviteView from '@/views/auth/AcceptInviteView.vue'
import AccountCreationSuccessView from '@/views/auth/create-account/AccountCreationSuccessView.vue'
import AccountDeactivate from '@/views/auth/AccountDeactivate.vue'
import AccountFreezeUnlockView from '@/views/auth/account-freeze/AccountFreezeUnlockView.vue'
import AccountFreezeView from '@/views/auth/account-freeze/AccountFreezeView.vue'
import AccountInstructions from '@/components/auth/create-account/non-bcsc/AccountInstructions.vue'
import AccountLoginOptionsChooser from '@/views/auth/AccountLoginOptionsChooser.vue'
import AccountLoginOptionsInfo from '@/views/auth/AccountLoginOptionsInfo.vue'
import AccountSetupLanding from '@/views/auth/create-account/AccountSetupLanding.vue'
import AccountSwitching from '@/views/auth/AccountSwitching.vue'
import AccountUnlockSuccessView from '@/views/auth/account-freeze/AccountUnlockSuccessView.vue'
import AdminDashboardView from '@/views/auth/staff/AdminDashboardView.vue'
import AffidavitDownload from '@/components/auth/create-account/non-bcsc/AffidavitDownload.vue'
import AuthenticationOptionsView from '@/views/auth/AuthenticationOptionsView.vue'
import BusinessProfileView from '@/views/auth/BusinessProfileView.vue'
import CcPaymentReturnView from '@/views/pay/CcPaymentReturnView.vue'
import CcPaymentView from '@/views/pay/CcPaymentView.vue'
import ChooseAuthMethodView from '@/views/auth/ChooseAuthMethodView.vue'
import ConfigHelper from '@/util/config-helper'
import CreateAccountView from '@/views/auth/CreateAccountView.vue'
import DashboardView from '@/views/auth/DashboardView.vue'
import DecideBusinessView from '@/views/auth/home/DecideBusinessView.vue'
import DuplicateAccountWarningView from '@/views/auth/create-account/DuplicateAccountWarningView.vue'
import DuplicateTeamWarningView from '@/views/auth/DuplicateTeamWarningView.vue'
import EntityManagement from '@/components/auth/manage-business/EntityManagement.vue'
import GLCodesListView from '@/views/auth/staff/GLCodesListView.vue'
import GovmAccountCreationSuccessView from '@/views/auth/create-account/GovmAccountCreationSuccessView.vue'
import GovmAccountSetupView from '@/views/auth/create-account/GovmAccountSetupView.vue'
import HomeView from '@/views/auth/home/HomeView.vue'
import IncorpOrRegisterView from '@/views/auth/home/IncorpOrRegisterView.vue'
import KeyCloakService from 'sbc-common-components/src/services/keycloak.services'
import LeaveTeamLandingView from '@/views/auth/LeaveTeamLandingView.vue'
import LoginView from '@/views/auth/LoginView.vue'
import MaintainBusinessView from '@/views/auth/home/MaintainBusinessView.vue'
import NonBcscAccountCreationSuccessView from '@/views/auth/create-account/non-bcsc/NonBcscAccountCreationSuccessView.vue'
import NonBcscAccountSetupView from '@/views/auth/create-account/non-bcsc/NonBcscAccountSetupView.vue'
import NonBcscAdminInviteSetupView from '@/views/auth/create-account/non-bcsc/NonBcscAdminInviteSetupView.vue'
import NonBcscInfoView from '@/views/auth/create-account/non-bcsc/NonBcscInfoView.vue'
import PADTermsAndConditionsView from '@/views/auth/PADTermsAndConditionsView.vue'
import PageNotFound from '@/views/auth/PageNotFound.vue'
import PaymentReturnView from '@/views/pay/PaymentReturnView.vue'
import PaymentView from '@/views/pay/PaymentView.vue'
import PendingApprovalView from '@/views/auth/PendingApprovalView.vue'
import PriceListView from '@/views/auth/PriceListView.vue'
import ProfileDeactivatedView from '@/views/auth/ProfileDeactivatedView.vue'
import RequestNameView from '@/views/auth/home/RequestNameView.vue'
import RestrictedProductView from '@/views/auth/RestrictedProductView.vue'
import ReviewAccountView from '@/views/auth/staff/ReviewAccountView.vue'
import { RouteConfig } from 'vue-router'
import SetupAccountSuccessView from '@/views/auth/staff/SetupAccountSuccessView.vue'
import SetupAccountView from '@/views/auth/staff/SetupAccountView.vue'
import SetupGovmAccountView from '@/views/auth/staff/SetupGovmAccountView.vue'
import SigninView from '@/views/auth/SigninView.vue'
import SignoutView from '@/views/auth/SignoutView.vue'
import StaffActiveAccountsTable from '@/components/auth/staff/account-management/StaffActiveAccountsTable.vue'
import StaffDashboardView from '@/views/auth/staff/StaffDashboardView.vue'
import StaffPendingAccountInvitationsTable from '@/components/auth/staff/account-management/StaffPendingAccountInvitationsTable.vue'
import StaffPendingAccountsTable from '@/components/auth/staff/account-management/StaffPendingAccountsTable.vue'
import StaffRejectedAccountsTable from '@/components/auth/staff/account-management/StaffRejectedAccountsTable.vue'
import StaffSuspendedAccountsTable from '@/components/auth/staff/account-management/StaffSuspendedAccountsTable.vue'
import TermsOfServiceDeclineView from '@/views/auth/TermsOfServiceDeclineView.vue'
import TermsOfServiceView from '@/views/auth/TermsOfServiceView.vue'
import UnauthorizedView from '@/views/auth/UnauthorizedView.vue'
import UpdateAccountView from '@/views/auth/create-account/UpdateAccountView.vue'
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

function mapOrgDetails (route: any) {
  let orgName = route.params.orgName
  try {
    orgName = window.atob(orgName)
  } catch (e) {
    // older invitations.Ignore.org name wont be base 64 for old invitations.
  }

  return {
    token: route.params.token,
    loginSource: route.params.loginSource,
    orgName: orgName
  }
}

function mapPendingDetails (route: any) {
  let orgName = route.params.teamName
  try {
    orgName = window.atob(orgName)
  } catch (e) {
    // older invitations.Ignore.org name wont be base 64 for old invitations.
  }

  return {
    teamName: orgName,
    pendingAffidavit: route.params.pendingAffidavit
  }
}

function isStaff (): boolean {
  const kcUserProfile = KeyCloakService.getUserInfo()
  return kcUserProfile?.roles?.includes(Role.Staff) || false
}

export function getRoutes (): RouteConfig[] {
  const accountSettings = () => import(/* webpackChunkName: "account-settings" */ '../views/auth/AccountSettings.vue')
  const accountInfo = () => import(/* webpackChunkName: "account-settings" */ '../components/auth/account-settings/account-info/AccountInfo.vue')
  const teamManagement = () => import(/* webpackChunkName: "account-settings" */ '../components/auth/account-settings/team-management/TeamManagement.vue')
  const accountLoginOption = () => import(/* webpackChunkName: "account-settings" */ '../components/auth/account-settings/login-options/AccountSettingsLoginOption.vue')
  const accountPaymentOption = () => import(/* webpackChunkName: "account-settings" */ '../components/auth/account-settings/payment/AccountPaymentMethods.vue')
  const transaction = () => import(/* webpackChunkName: "account-settings" */ '../components/auth/account-settings/transaction/Transactions.vue')
  const statements = () => import(/* webpackChunkName: "account-settings" */ '../components/auth/account-settings/statement/Statements.vue')
  const productPackage = () => import(/* webpackChunkName: "product-settings" */ '../components/auth/account-settings/product/ProductPackage.vue')
  const activityLog = () => import(/* webpackChunkName: "activity-log" */ '../components/auth/account-settings/activity-log/ActivityLog.vue')
  const developerAccess = () => import(/* webpackChunkName: "developer-access" */ '../components/auth/account-settings/advance-settings/DeveloperAccess.vue')

  const routes = [
    { path: '/', name: 'root', redirect: 'home' },
    {
      path: '/home',
      component: HomeView,
      children: [
        {
          path: '',
          name: 'home',
          redirect: 'decide-business'
        },
        {
          path: 'decide-business',
          name: 'decide-business',
          component: DecideBusinessView,
          meta: {
            breadcrumb: [
              RegistryHomeBreadcrumb,
              {
                text: 'Business Registry Home',
                to: { name: 'decide-business' }
              }
            ],
            showNavBar: true
          }
        },
        {
          path: 'request-name',
          name: 'request-name',
          component: RequestNameView,
          meta: {
            breadcrumb: [
              RegistryHomeBreadcrumb,
              {
                text: 'Business Registry Home',
                to: { name: 'request-name' }
              }
            ],
            showNavBar: true
          }
        },
        {
          path: 'incorporate-or-register',
          name: 'incorporate-or-register',
          component: IncorpOrRegisterView,
          meta: {
            breadcrumb: [
              RegistryHomeBreadcrumb,
              {
                text: 'Business Registry Home',
                to: { name: 'incorporate-or-register' }
              }
            ],
            showNavBar: true
          }
        },
        {
          path: 'maintain-business',
          name: 'maintain-business',
          component: MaintainBusinessView,
          meta: {
            breadcrumb: [
              RegistryHomeBreadcrumb,
              {
                text: 'Business Registry Home',
                to: { name: 'maintain-business' }
              }
            ],
            showNavBar: true
          }
        }
      ]
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
            requiresAuth: true,
            requiresActiveAccount: true,
            breadcrumb: isStaff()
              ? [StaffDashboardBreadcrumb, StaffBusinessRegistryBreadcrumb]
              : [RegistryDashboardBreadcrumb, MyBusinessRegistryBreadcrumb]
          }
        }]
    },
    {
      path: '/account/:orgId/settings',
      name: 'account-settings',
      component: accountSettings,
      meta: {
        requiresAuth: true,
        requiresProfile: true,
        requiresActiveAccount: true
      },
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
        },
        {
          path: 'product-settings',
          name: 'product-settings',
          component: productPackage
        },
        {
          path: 'activity-log',
          name: 'activity-log',
          component: activityLog
        },
        {
          path: 'developer-access',
          name: 'developer-access',
          component: developerAccess
        }
      ]
    },
    {
      path: '/account-switching',
      name: 'accountswitching',
      component: AccountSwitching,
      props: (route) => ({ redirectToUrl: route.query.redirectToUrl, accountid: route.query.accountid }),
      meta: { requiresAuth: true }
    },
    {
      path: '/price-list',
      name: 'price-list',
      component: PriceListView,
      meta: { requiresAuth: false, showNavBar: false }
    },
    {
      path: '/setup-account',
      name: 'setupaccount',
      component: AccountSetupLanding,
      props: (route) => ({ redirectToUrl: route.query.redirectToUrl, skipConfirmation: route.query.skipConfirmation }),
      meta: { requiresAuth: true, requiresProfile: true }
    },
    {
      path: '/setup-non-bcsc-account/:orgId?',
      name: 'setup-non-bcsc-account',
      component: NonBcscAccountSetupView,
      props: true,
      meta: { requiresAuth: true, requiresProfile: true }
    },
    {
      path: '/setup-govm-account',
      name: 'setupaccount',
      component: GovmAccountSetupView,
      props: true,
      meta: { requiresAuth: true, requiresProfile: true }
    },
    {
      path: '/update-account',
      name: 'updateaccount',
      component: UpdateAccountView,
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
      path: '/setup-account-success',
      name: 'setup-account-success',
      component: AccountCreationSuccessView,
      meta: { requiresAuth: true, requiresProfile: true }
    },
    {
      path: '/setup-govm-account-success',
      name: 'setup-govm-account-success',
      component: GovmAccountCreationSuccessView,
      meta: { requiresAuth: true, requiresProfile: true }
    },
    {
      path: '/account-freeze-nsf',
      name: 'account-freeze-nsf',
      component: AccountFreezeUnlockView,
      props: true,
      meta: { requiresAuth: true, requiresProfile: true }
    },
    {
      path: '/account-freeze',
      name: 'account-freeze',
      component: AccountFreezeView,
      props: true,
      meta: { requiresAuth: true, requiresProfile: true }
    },
    {
      path: '/account-unlock-success',
      name: 'account-unlock-success',
      component: AccountUnlockSuccessView,
      props: true,
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
      path: '/confirmtoken/:token/:loginSource?',
      name: 'confirmtoken',
      component: AcceptInviteView,
      props: true,
      meta: { requiresAuth: true, disabledRoles: [Role.Staff] }
    },
    {
      path: '/upload-affidavit/:token?',
      name: 'uploadaffidavit',
      component: NonBcscAdminInviteSetupView,
      props: true,
      meta: { requiresAuth: true, disabledRoles: [Role.Staff] }
    },
    // For reupload affidavit of BCeID Admin flow - same component different route
    {
      path: '/re-upload-affidavit/:orgId?/:membershipId?',
      name: 'reuploadaffidavit',
      component: NonBcscAdminInviteSetupView,
      props: true,
      meta: { requiresAuth: true, disabledRoles: [Role.Staff] }
    },
    {
      path: '/:orgName/validatetoken/:loginSource/:token',
      component: AcceptInviteLandingView,
      props: mapOrgDetails,
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
      meta: { requiresAuth: true, requiresProfile: true, requiresActiveAccount: true }
    },
    {
      path: '/makepayment/:paymentId/:redirectUrl',
      name: 'makepayment',
      component: PaymentView,
      props: true,
      meta: { requiresAuth: false }
    },
    {
      path: '/make-cc-payment/:paymentId/transactions/:redirectUrl',
      name: 'make-cc-payment',
      component: CcPaymentView,
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
      path: '/return-cc-payment/:paymentId/transaction/:transactionId',
      name: 'return-cc-payment',
      component: CcPaymentReturnView,
      props: mapReturnPayVars,
      meta: { requiresAuth: false }
    },
    {
      path: Pages.ADMIN,
      name: 'admin',
      redirect: Pages.ADMIN_DASHBOARD
    },
    {
      path: Pages.ADMIN_DASHBOARD,
      component: AdminDashboardView,
      props: true,
      meta: { requiresAuth: true, allowedRoles: [Role.AdminEdit] }
    },
    {
      path: Pages.STAFF_DASHBOARD,
      component: StaffDashboardView,
      props: true,
      meta: { requiresAuth: true, allowedRoles: [Role.Staff] },
      children: [
        {
          path: '',
          name: 'staff-dashboard',
          redirect: 'active'
        },
        {
          path: 'active',
          name: 'active',
          component: StaffActiveAccountsTable,
          meta: {
            breadcrumb: [
              {
                text: StaffDashboardBreadcrumb.text,
                to: { name: 'active' }
              }
            ],
            showNavBar: true
          }
        },
        {
          path: 'invitations',
          name: 'invitations',
          component: StaffPendingAccountInvitationsTable,
          meta: {
            breadcrumb: [
              {
                text: StaffDashboardBreadcrumb.text,
                to: { name: 'invitations' }
              }
            ],
            showNavBar: true
          }
        },
        {
          path: 'review',
          name: 'review',
          component: StaffPendingAccountsTable,
          meta: {
            breadcrumb: [
              {
                text: StaffDashboardBreadcrumb.text,
                to: { name: 'review' }
              }
            ],
            showNavBar: true
          }
        },
        {
          path: 'rejected',
          name: 'rejected',
          component: StaffRejectedAccountsTable,
          meta: {
            breadcrumb: [
              {
                text: StaffDashboardBreadcrumb.text,
                to: { name: 'rejected' }
              }
            ],
            showNavBar: true
          }
        },
        {
          path: 'suspended',
          name: 'suspended',
          component: StaffSuspendedAccountsTable,
          meta: {
            breadcrumb: [
              {
                text: StaffDashboardBreadcrumb.text,
                to: { name: 'suspended' }
              }
            ],
            showNavBar: true
          }
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
      path: '/login',
      name: 'login',
      component: LoginView,
      props: true,
      meta: { requiresAuth: false }
    },
    {
      path: '/account/:orgId/restricted-product/:productName?',
      name: 'RestrictedProduct',
      component: RestrictedProductView,
      props: true,
      meta: { requiresAuth: true }
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
      props: mapPendingDetails,
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
      path: '/staff-govm-setup-account',
      name: 'staffGovmsetupaccount',
      component: SetupGovmAccountView,
      props: true,
      meta: { requiresAuth: true, allowedRoles: [Role.Staff] }
    },
    {
      path: '/staff-setup-account-success/:accountType?/:accountName?',
      name: 'staffsetupaccountsuccess',
      component: SetupAccountSuccessView,
      props: true,
      meta: { requiresAuth: true, allowedRoles: [Role.Staff] }
    },
    {
      path: '/userprofileterms/:token?/:redirectUri?',
      name: 'userprofileterms',
      props: true,
      component: TermsOfServiceView,
      meta: { requiresAuth: true }
    },
    {
      path: '/PAD-terms-and-conditions',
      name: 'padtermsandconditions',
      props: true,
      component: PADTermsAndConditionsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/account-deactivate',
      name: 'account-deactivate',
      props: true,
      component: AccountDeactivate,
      meta: { requiresAuth: true }
    },
    {
      path: '/duplicate-account-warning',
      component: DuplicateAccountWarningView,
      meta: { requiresAuth: true, requiresProfile: true, requiresActiveAccount: true },
      name: 'duplicateaccountwarning',
      props: (route) => ({ redirectToUrl: route.query.redirectToUrl })
    },
    { path: '*', name: 'notfound', component: PageNotFound }
  ]

  return routes
}
