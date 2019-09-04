import PasscodeForm from '@/components/auth/PasscodeForm.vue'
import Vuex from 'vuex'
import { mount, createLocalVue } from '@vue/test-utils'
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'

Vue.use(Vuetify)
Vue.use(VueRouter)

jest.mock('axios', () => ({
  post: jest.fn(() => Promise.resolve({ data: { access_token: 'abcd', refresh_token: 'efgh', registries_trace_id: '12345abcde' } }))
}))

describe('PasscodeForm.vue', () => {
  let cmp
  var ob = {
    'VUE_APP_ROOT_API': 'https://localhost:8080/api/v1/11',
    'VUE_APP_COPS_REDIRECT_URL': 'https://coops-dev.pathfinder.gov.bc.ca/',
    'VUE_APP_PAY_ROOT_API': 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1',
    'VUE_APP_FLAVOR': 'mvp'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(ob)
  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({
      strict: true
    })

    const $t = () => {}

    let vuetify = new Vuetify({})

    cmp = mount(PasscodeForm, {
      store,
      localVue,
      vuetify,
      mocks: { $t }
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('passcode screen login button exists', () => {
    expect(cmp.find('.sign-in-btn').text().startsWith('Sign In')).toBeTruthy()
    expect(cmp.isVueInstance()).toBeTruthy()
  })

  it('passcode and business number is empty', () => {
    expect(cmp.vm.businessNumber).toBe('')
    expect(cmp.vm.passcode).toBe('')
  })

  it('login button click invokes login method', () => {
    const stub = jest.fn()
    cmp.setMethods({ login: stub })
    cmp.find('.sign-in-btn').trigger('click')
    expect(cmp.vm.login).toBeCalled()
  })

  it('login button click invokes isFormValid method', () => {
    const stub = jest.fn()
    cmp.setMethods({ isFormValid: stub })
    cmp.find('.sign-in-btn').trigger('click')
    expect(cmp.vm.isFormValid).toBeCalled()
  })
})
