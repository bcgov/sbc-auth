import { createLocalVue, mount } from '@vue/test-utils'

import { AccountStatus } from '@/util/constants'
import AccountSuspendedView from '@/views/auth/account-freeze/AccountSuspendedView.vue'
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

describe('AccountSuspendedView.vue', () => {
  let wrapper: any
  let userModule: any

  beforeEach(() => {
    sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockSession)
    const localVue = createLocalVue()
    localVue.use(Vuex)
    wrapper = mount(AccountSuspendedView, {
      localVue,
      router,
      vuetify,
      mocks: {
        $t: (mock) => mock
      },
      propsData: {
        isAdmin: false
      }
    })
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('Validate is-user message', () => {
    expect(wrapper.find('h1').text()).toBe('Account Suspended')
    expect(wrapper.find('[data-test="div-is-user"]').text()).toBe('Your account is suspended. Please contact the account administrator')
    expect(wrapper.find('[data-test="div-is-admin"]').exists()).toBeFalsy()
  })

  it('Validate is-admin message', () => {
    wrapper.setProps({ isAdmin: true })
    expect(wrapper.find('h1').text()).toBe('Account Suspended')
    expect(wrapper.find('[data-test="div-is-admin"]').text()).toBe('Your account is suspended. For more information, please contact the BC Online Partnership Office at: Email: bconline@gov.bc.ca Telephone: 1-800-663-6102')
    expect(wrapper.find('[data-test="div-is-user"]').exists()).toBeFalsy()
  })
})
