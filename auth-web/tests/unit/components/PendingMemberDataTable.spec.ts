import { createLocalVue, mount } from '@vue/test-utils'
import OrgModule from '@/store/modules/org'
import PendingMemberDataTable from '@/components/auth/account-settings/team-management/PendingMemberDataTable.vue'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)
Vue.use(VueI18n)
const vuetify = new Vuetify({})

jest.mock('../../../src/services/bcol.services')

describe('PendingMemberDataTable.vue', () => {
  let localVue
  let store

  const config = {
    AUTH_API_URL: 'https://localhost:8080/api/v1/11',
    PAY_API_URL: 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
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
    const wrapper = mount(PendingMemberDataTable, {
      store,
      vuetify,
      localVue,
      mocks: { $t }
    })
    expect(wrapper.find('.user-list')).toBeTruthy()
    wrapper.destroy()
  })
})
