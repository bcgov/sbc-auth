import { Wrapper, createLocalVue, shallowMount } from '@vue/test-utils'
import StaffActiveAccountsTable from '@/components/auth/staff/account-management/StaffActiveAccountsTable.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('StaffActiveAccountsTable.vue', () => {
  let wrapper: Wrapper<StaffActiveAccountsTable>

  const config = {
    'AUTH_API_URL': 'https://localhost:8080/api/v1/11',
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const staffModule = {
      namespaced: true,
      state: {
        suspendedStaffOrgs: [
          {
            'modified': '2020-12-10T21:05:06.144977+00:00',
            'name': 'NEW BC ONLINE TECH TEAM',
            'orgType': 'PREMIUM',
            'orgStatus': 'ACTIVE',
            'products': [
              2342,
              2991
            ],
            'statusCode': 'ACTIVE',
            'suspendedOn': '2020-12-01T17:52:03.747200+00:00'
          }
        ]
      },
      actions: {
        searchOrgs: jest.fn()
      }
    }

    const orgModule = {
      namespaced: true,
      state: {},
      actions: {
        syncMembership: jest.fn(),
        addOrgSettings: jest.fn(),
        syncOrganization: jest.fn()
      }
    }

    const vuetify = new Vuetify({})

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        staff: staffModule,
        org: orgModule
      }
    })

    const $t = () => ''
    wrapper = shallowMount(StaffActiveAccountsTable, {
      store,
      localVue,
      vuetify,
      mocks: { $t }
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })
  // TOFIX fix orgs undefiend
  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('Should have data table', () => {
    expect(wrapper.find('.account-list')).toBeTruthy()
  })
})
