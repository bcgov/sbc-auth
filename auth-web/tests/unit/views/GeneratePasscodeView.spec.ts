import { createLocalVue, mount } from '@vue/test-utils'

import GeneratePasscodeView from '@/views/auth/staff/GeneratePasscodeView.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

const mockSession = {
  'NRO_URL': 'Mock NRO URL',
  'NAME_REQUEST_URL': 'Mock Name Request URL'
}

Vue.use(Vuetify)
Vue.use(VueRouter)
document.body.setAttribute('data-app', 'true')

const router = new VueRouter()
const vuetify = new Vuetify({})

describe('GeneratePasscodeView.vue', () => {
  let wrapper: any

  beforeEach(() => {
    sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockSession)
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const $t = () => ''

    const store = new Vuex.Store({
      state: {},
      strict: false
    })

    wrapper = mount(GeneratePasscodeView, {
      store,
      localVue,
      router,
      vuetify,
      mocks: { $t }
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

  it('contains email address input to send', () => {
    expect(wrapper.find('[data-test="text-email-address"]')).toBeTruthy()
    expect(wrapper.find('[data-test="text-confirm-email-address"]')).toBeTruthy()
  })

  it('email Rules', () => {
    wrapper.vm.isResetPasscode = false
    wrapper.vm.emailAddress = 'test3@gmail.com'
    wrapper.vm.confirmedEmailAddress = 'test22@gmail.com'
    let result = wrapper.vm.emailMustMatch()
    expect(result).toEqual('Email addresses must match')
    wrapper.vm.emailAddress = 'test@gmail.com'
    wrapper.vm.confirmedEmailAddress = 'test@gmail.com'
    result = wrapper.vm.emailMustMatch()
    expect(result).toEqual('')
  })
})
