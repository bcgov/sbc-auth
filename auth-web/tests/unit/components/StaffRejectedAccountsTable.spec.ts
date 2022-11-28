import { Wrapper, createLocalVue, shallowMount } from '@vue/test-utils'
import StaffRejectedAccountsTable from '@/components/auth/staff/account-management/StaffRejectedAccountsTable.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('StaffRejectedAccountsTable.vue', () => {
  let wrapper: Wrapper<StaffRejectedAccountsTable>

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const staffModule = {
      namespaced: true,
      state: {
        rejectedStaffOrgs: [
          {
            'modified': '2020-12-10T22:05:06.144977+00:00',
            'name': 'NEW BC ONLINE TECH TEAM',
            'orgType': 'BASIC',
            'orgStatus': 'ACTIVE',
            'products': [
              2341,
              2992
            ],
            'statusCode': 'ACTIVE'
          }
        ]
      },
      actions: {
        rejectedStaffOrgs: jest.fn()
      }
    }

    const vuetify = new Vuetify({})

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        staff: staffModule
      }
    })

    const $t = () => ''
    wrapper = shallowMount(StaffRejectedAccountsTable, {
      store,
      localVue,
      vuetify,
      mocks: { $t }
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance and has a data table', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
    expect(wrapper.find('.user-list')).toBeTruthy()
  })
})
