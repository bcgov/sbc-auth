import { createLocalVue, shallowMount } from '@vue/test-utils'
import MemberDataTable from '@/components/auth/MemberDataTable.vue'
import OrgModule from '@/store/modules/org'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)
Vue.use(VueI18n)

jest.mock('../../../src/services/bcol.services')

describe('MemberDataTable.vue', () => {
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
        pendingOrgInvitations: [],
        currentOrganization: {},
        activeOrgMembers: [{ 'membershipTypeCode': 'OWNER', 'user': { 'username': 'test' } }],
        pendingOrgMembers: [{ 'membershipTypeCode': 'OWNER', 'user': { 'username': 'test' } }]
      },
      actions: {
        createInvitation: jest.fn(),
        resendInvitation: jest.fn()
      },
      mutations: {
        resetInvitations: jest.fn()
      },
      getters: OrgModule.getters
    }
    const userModule = {
      namespaced: true,
      state: {
        currentUser: { 'userName': 'test' }
      }
    }
    const businessModule = {
      namespaced: true,
      state: {
        businesses: []
      }
    }

    store = new Vuex.Store({
      strict: false,
      modules: {
        org: orgModule,
        user: userModule,
        business: businessModule
      }
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('Mounting works', () => {
    const $t = () => 'test'
    const wrapper = shallowMount(MemberDataTable, {
      store,
      localVue,
      mocks: { $t }
    })
    expect(wrapper.find('.user-list')).toBeTruthy()
  })
})
