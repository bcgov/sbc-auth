import { createLocalVue, shallowMount } from '@vue/test-utils'

import AccountPaymentMethods from '@/components/auth/account-settings/payment/AccountPaymentMethods.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

// Prevent error redundant navigation.
const originalPush = VueRouter.prototype.push
VueRouter.prototype.push = function push(location) {
  return originalPush.call(this, location).catch(() => {})
}

describe('AccountPaymentMethods.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(VueRouter)

    const router = new VueRouter()
    const orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {
          name: 'new org',
          orgType: 'STAFF'
        }
      },
      action: {
        syncAddress: vi.fn()
      }
    }
    const businessModule = {
      namespaced: true,
      state: {
        businesses: []

      },
      action: {
        addBusiness: vi.fn()
      }
    }

    const userModule: any = {
      namespaced: true,
      state: {
        currentUser: {
          firstName: 'Nadia',
          lastName: 'Woodie'
        }
      }
    }

    const store = new Vuex.Store({
      strict: false,
      modules: {
        org: orgModule,
        business: businessModule,
        user: userModule
      }
    })

    wrapperFactory = (propsData) => {
      return shallowMount(AccountPaymentMethods, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {
          ...propsData
        }
      })
    }

    wrapper = wrapperFactory({})
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
  })

  afterAll(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the components properly and address is being shown', () => {
    expect(wrapper.findComponent(AccountPaymentMethods).exists()).toBe(true)
  })

  it('renders proper header content', () => {
    expect(wrapper.find('h2').text()).toBe('Payment Methods')
  })

  it('renders sub text content', () => {
    expect(wrapper.find('p').text()).toBe('Manage your payment method for this account.')
  })
})
