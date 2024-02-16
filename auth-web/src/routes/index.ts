/* eslint-disable no-console */
import {
  ALLOWED_URIS_FOR_PENDING_ORGS,
  Account,
  AccountStatus,
  LoginSource,
  Pages,
  Permission,
  Role, SessionStorageKeys
} from '@/util/constants'
import { Member, MembershipStatus, MembershipType, Organization } from '@/models/Organization'
import { AccountSettings } from '@/models/account-settings'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import KeyCloakService from 'sbc-common-components/src/services/keycloak.services'
import Router from 'vue-router'
import { User } from '@/models/user'
import Vue from 'vue'
import { getRoutes } from './router'
import store from '@/stores/vuex'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

Vue.use(Router)

const router = new Router({
  mode: 'history',
  base: import.meta.env.BASE_URL
})

router.addRoutes(getRoutes())

router.beforeEach(async (to, from, next) => {
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
        path: '/login',
        query: { redirect: to.fullPath }
      })
    }
  }

  // Enforce navigation guards are checked before navigating anywhere else
  // Remove Vuex with Vue3 upgrade. - Will be replaced by Pinia onAction.
  if (store.getters.loading) {
    await new Promise(resolve => {
      const unsubscribeFn = store.subscribe(mutation => {
        if (mutation.type === 'loadComplete') {
          unsubscribeFn()
          resolve(null)
        }
      })
    })
  }
  proceed()

  function proceed () {
    const orgStore = useOrgStore()
    const userStore = useUserStore()
    const userProfile: User = userStore.userProfile
    const currentAccountSettings: AccountSettings = orgStore.currentAccountSettings
    const currentOrganization: Organization = orgStore.currentOrganization
    const currentMembership: Member = orgStore.currentMembership
    const currentUser: KCUserProfile = userStore.currentUser
    const permissions: string[] = orgStore.permissions
    if (to.path === `/${Pages.LOGIN}` && currentUser) {
      // If the user came back from login page and is already logged in
      // redirect to redirect path
      return next({
        path: `${to.query.redirect as string}` || '/'
      })
    } else {
      if (to.matched.some(record => record.meta.isPremiumOnly)) {
        const currentOrganization: Organization = orgStore.currentOrganization
        const currentMembership: Member = orgStore.currentMembership
        const currentUser: KCUserProfile = userStore.currentUser
        // redirect to unauthorized page if the account selected is not Premium
        if (!(currentOrganization?.orgType === Account.PREMIUM &&
          [MembershipType.Admin, MembershipType.Coordinator].includes(currentMembership.membershipTypeCode)) &&
          currentUser?.loginSource !== LoginSource.IDIR) {
          return next({
            path: '/unauthorized',
            query: { redirect: to.fullPath }
          })
        }
      }
      if (to.matched.some(record => record.meta.requiresProfile) &&
        !userProfile?.userTerms?.isTermsOfUseAccepted) {
        switch (currentUser?.loginSource) {
          case LoginSource.IDIR:
            break
          case LoginSource.BCSC:
          case LoginSource.BCROS:
          case LoginSource.BCEID: {
            // eslint-disable-next-line no-console
            console.log('[Navigation Guard] Redirecting user to TOS since user has not accepted one')
            // if there's redirectUri in query string, keep existing redirectUri, otherwise use current location
            const urlParams = new URLSearchParams(window.location.search)
            let uriRedirectTo = urlParams.get('redirectUri')
            if (uriRedirectTo === '' || uriRedirectTo === null) {
              uriRedirectTo = window.location.pathname.replace(import.meta.env.VUE_APP_PATH, '')
            }
            return next({
              path: `/${Pages.USER_PROFILE_TERMS}`,
              query: { redirectUri: `${uriRedirectTo}` }
            })
          }
          default:
            return next({
              path: '/'
            })
        }
      }
    }

    if (to.path === `/${Pages.ACCOUNT_FREEZE}`) {
      console.log('[NG] Redirecting user to Account Freeze message since the account is temporarly suspended.')
      // checking for access page
      if (permissions.some(code => code !== Permission.MAKE_PAYMENT)) {
        return next({ path: `/${Pages.ACCOUNT_FREEZE_UNLOCK}` })
      }
    }
    // need to check for govm account also. so we are checking roles
    if (to.matched.some(record => record.meta.requiresActiveAccount) &&
        (currentUser.loginSource === LoginSource.BCSC || currentUser.loginSource === LoginSource.BCEID ||
          currentUser.roles.includes(Role.GOVMAccountUser))) {
      // if (currentOrganization?.statusCode === AccountStatus.NSF_SUSPENDED) {
      if ([AccountStatus.NSF_SUSPENDED, AccountStatus.SUSPENDED].some(status => status === currentOrganization?.statusCode)) {
        console.log('[NG] Redirecting user to Account Freeze message since the account is temporarly suspended.')
        if (permissions.some(code => code === Permission.MAKE_PAYMENT)) {
          return next({ path: `/${Pages.ACCOUNT_FREEZE_UNLOCK}` })
        } else {
          return next({ path: `/${Pages.ACCOUNT_FREEZE}` })
        }
      } else if (currentOrganization?.statusCode === AccountStatus.PENDING_STAFF_REVIEW) {
        const substringCheck = (element:string) => to.path.indexOf(element) > -1
        const isAllowedUrl = ALLOWED_URIS_FOR_PENDING_ORGS.findIndex(substringCheck) > -1
        if (!isAllowedUrl) {
          console.log('[NG] Redirecting user to PENDING_APPROVAL since user has pending affidavits')
          // TODO put the account name back once its avaialable ;may be needs a fix in sbc-common
          return next(
            { path: `/${Pages.PENDING_APPROVAL}/${encodeURIComponent(btoa(currentAccountSettings?.label))}/true` })
        }
      } else if (currentAccountSettings && [MembershipStatus.PendingStaffReview, MembershipStatus.Pending]
        .includes(currentMembership?.membershipStatus)) {
        console.log('[NG] Redirecting user to PENDING_APPROVAL/STAFF_REVIEW since users membership status is pending')
        return next({ path: `/${Pages.PENDING_APPROVAL}/${encodeURIComponent(btoa(currentAccountSettings?.label))}` })
      } else if (!currentOrganization || currentMembership?.membershipStatus !== MembershipStatus.Active) {
        console.log('[NG] Redirecting user to Create Account since users nerither has account nor an active status')
        switch (currentUser?.loginSource) {
          case LoginSource.BCSC:
            return next({ path: `/${Pages.CREATE_ACCOUNT}` })
          case LoginSource.BCEID:
            return next({ path: `/${Pages.CREATE_NON_BCSC_ACCOUNT}` })
        }
      } else if (orgStore.needMissingBusinessDetailsRedirect) {
        return next({ path: `/${Pages.UPDATE_ACCOUNT}` })
      }
    }
    next()
  }
})

export default router
