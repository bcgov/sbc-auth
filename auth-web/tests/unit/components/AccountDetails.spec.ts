import { createLocalVue, shallowMount } from '@vue/test-utils'

import AccountDetails from '@/components/auth/account-settings/account-info/AccountDetails.vue'

import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import can from '@/directives/can'

Vue.use(Vuetify)
Vue.use(VueRouter)

const vuetify = new Vuetify({})

document.body.setAttribute('data-app', 'true')

describe('AccountDetails.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.directive('can', can)
    const codesModule = {
      namespaced: true,
      state: {
        businessSizeCodes: [
          { code: '0-1', default: true, desc: '1 Employee' },
          { code: '2-5', default: false, desc: '2-5 Employees' }
        ],
        businessTypeCodes: [
          { code: 'BIZ', default: false, desc: 'GENERAL BUSINESS' }
        ]
      },
      actions: {
        getBusinessSizeCodes: jest.fn(),
        getBusinessTypeCodes: jest.fn()
      }
    }

    const store = new Vuex.Store({
      strict: false,
      modules: {
        codes: codesModule
      }
    })

    wrapperFactory = propsData => {
      return shallowMount(AccountDetails, {
        localVue,
        store,
        vuetify,
        propsData: {
          ...propsData
        }
      })
    }

    wrapper = wrapperFactory({ accountDetails: {
      name: 'QQ COUNTERTOP',
      branchName: '22',
      businessType: 'BIZAC',
      businessSize: '0-1'
    },
    viewOnlyMode: false
    })
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('renders the components properly ', () => {
    expect(wrapper.find(AccountDetails).exists()).toBe(true)
  })

  it('renders proper header content', () => {
    expect(wrapper.find('[data-test="title"]').text()).toBe('Account Details')
  })

  it('Show edit icon when passing props', async () => {
    expect(wrapper.find('[data-test="btn-edit"]').exists()).toBe(false)
    await wrapper.setProps({ viewOnlyMode: true })
    expect(wrapper.find('[data-test="btn-edit"]').exists()).toBe(true)
  })
})
