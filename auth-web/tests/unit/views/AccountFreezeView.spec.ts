import { createLocalVue, mount } from '@vue/test-utils'

import AccountFreezeView from '@/views/auth/account-freeze/AccountFreezeView.vue'
import { AccountStatus } from '@/util/constants'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)
const router = new VueRouter()
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

const mockSession = {
  'NRO_URL': 'Mock NRO URL',
  'NAME_REQUEST_URL': 'Mock Name Request URL'
}

describe('AccountFreezeView.vue', () => {
  let wrapper: any
  let userModule: any

  beforeEach(() => {
    sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockSession)
    const localVue = createLocalVue()
    localVue.use(Vuex)

    userModule = {
      namespaced: true,
      state: {
        userProfile: {}
      },
      actions: {
        getUserProfile: jest.fn()
      }
    }

    const orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {
          statusCode: AccountStatus.NSF_SUSPENDED
        }
      }
    }

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        user: userModule,
        org: orgModule
      }
    })

    wrapper = mount(AccountFreezeView, {
      store,
      localVue,
      router,
      vuetify,
      mocks: {
        $t: (mock) => mock
      },
      computed: {
        isAccountStatusNsfSuspended: Boolean
      }
    })
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper).toBeTruthy()
  })

  it('should render page title', () => {
    expect(wrapper.find('h1').text()).toBe('Your Account is Temporarily Suspended')
  })

  it('should render page title icon', () => {
    expect(wrapper.find('.v-icon').exists()).toBe(true)
  })

  it('should render page title icon color correctly', () => {
    expect(wrapper.find('.v-icon').props().color).toBe('error')
  })
})
