import { Wrapper, createLocalVue, shallowMount } from '@vue/test-utils'
import StaffSuspendedAccountsTable from '@/components/auth/staff/account-management/StaffSuspendedAccountsTable.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('StaffSuspendedAccountsTable.vue', () => {
  let wrapper: Wrapper<StaffSuspendedAccountsTable>

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
            'orgStatus': 'NSF_SUSPENDED',
            'products': [
              2342,
              2991
            ],
            'statusCode': 'NSF_SUSPENDED',
            'suspendedOn': '2020-12-01T17:52:03.747200+00:00'
          }
        ]
      },
      actions: {
        syncSuspendedStaffOrgs: vi.fn(),
        searchOrgs: vi.fn()
      }
    }

    const orgModule = {
      namespaced: true,
      state: {},
      actions: {
        syncOrganization: vi.fn(),
        syncMembership: vi.fn(),
        addOrgSettings: vi.fn()
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
    wrapper = shallowMount(StaffSuspendedAccountsTable, {
      store,
      localVue,
      vuetify,
      mocks: { $t }
    })

    vi.resetModules()
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('Should have data table', () => {
    expect(wrapper.find('.account-list')).toBeTruthy()
  })
})
