import { createLocalVue, mount } from '@vue/test-utils'

import AccountSuspendedView from '@/views/auth/account-freeze/AccountSuspendedView.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import flushPromises from 'flush-promises'

const mockSession = {
  'NRO_URL': 'Mock NRO URL',
  'NAME_REQUEST_URL': 'Mock Name Request URL'
}

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

Vue.use(Vuetify)
Vue.use(VueRouter)
const router = new VueRouter()
const vuetify = new Vuetify({})

describe('AccountSuspendedView.vue', () => {
  let wrapper: any
  let userModule: any

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
  })

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

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('Validate is-user message', () => {
    expect(wrapper.find('h1').text()).toBe('Account Suspended')
    expect(wrapper.find('[data-test="div-is-user"]').text()).toBe('Your account is suspended. Please contact the account administrator')
    expect(wrapper.find('[data-test="div-is-admin"]').exists()).toBeFalsy()
  })

  it('Validate is-admin message', async () => {
    wrapper.setProps({ isAdmin: true })
    await flushPromises()
    expect(wrapper.find('h1').text()).toBe('Account Suspended')
    expect(wrapper.find('[data-test="div-is-admin"]').text()).toContain('Your account is suspended. For more information,')
    expect(wrapper.find('[data-test="div-is-admin"]').text()).toContain('please contact the BC Online Partnership Office at: Email: bconline@gov.bc.ca Telephone: 1-800-663-6102')
    expect(wrapper.find('[data-test="div-is-user"]').exists()).toBeFalsy()
  })
})
