import { createLocalVue, shallowMount } from '@vue/test-utils'
import InviteUsersForm from '@/components/auth/InviteUsersForm.vue'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)
Vue.use(VueI18n)

jest.mock('../../../src/services/bcol.services')

describe('InviteUsersForm.vue', () => {
  let localVue
  let store

  const config = {
    VUE_APP_ROOT_API: 'https://localhost:8080/api/v1/11',
    VUE_APP_COPS_REDIRECT_URL: 'https://coops-dev.pathfinder.gov.bc.ca/',
    VUE_APP_PAY_ROOT_API: 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)
  beforeEach(() => {
    localVue = createLocalVue()
    localVue.use(Vuex)
    const orgModule = {
      namespaced: true,
      state: {
        pendingOrgInvitations: [{
          id: 1,
          recipientEmail: 'myemail@mytestemail.com',
          sentDate: '2019-12-11T04:03:11.830365+00:00',
          membership: [],
          expiresOn: '2020-12-11T04:03:11.830365+00:00',
          status: 'pending'
        }],
        currentOrganization: {
          name: 'test org'
        },
        currentMembership: [{
          membershipTypeCode: 'OWNER',
          membershipStatus: 'ACTIVE',
          user: { username: 'test' } }],
        pendingOrgMembers: []
      },
      actions: {
        createInvitation: jest.fn(),
        resendInvitation: jest.fn()
      },
      mutations: {
        resetInvitations: jest.fn()
      }
    }

    const userModule = {
      namespaced: true,
      state: {
        currentUser: { userName: 'test' }
      }
    }

    const invitationModule = {
      namespaced: true,
      state: {
        invitations: []
      }
    }

    store = new Vuex.Store({
      strict: false,
      modules: {
        org: orgModule,
        user: userModule
      }
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('Mounting works', () => {
    const $t = () => 'test'
    const wrapper = shallowMount(InviteUsersForm, {
      store,
      localVue,
      mocks: { $t }
    })
    expect(wrapper.find('.invite-list')).toBeTruthy()
  })
})
