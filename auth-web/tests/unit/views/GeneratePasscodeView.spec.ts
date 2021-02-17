import { createLocalVue, mount } from '@vue/test-utils'

import GeneratePasscodeView from '@/views/auth/staff/GeneratePasscodeView.vue'
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

describe('GeneratePasscodeView.vue', () => {
  let wrapper: any

  beforeEach(() => {
    sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockSession)
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({
      state: {},
      strict: false
    })

    const $t = () => ''

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
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('contains title', () => {
    wrapper.vm.isDialogOpen = true
    expect(wrapper.find('[data-test="title-generate-passcode"]')).toBeTruthy()
    expect(wrapper.find('[data-test="title-generate-passcode"]').text()).toEqual('Generate Passcode')
  })

  it('contains email address input to send', () => {
    wrapper.vm.isDialogOpen = true
    expect(wrapper.find('[data-test="input-passcode-emailAddress-0"]')).toBeTruthy()
  })

  it('remove email address', () => {
    wrapper.vm.isDialogOpen = true
    const stub = jest.fn()
    wrapper.setMethods({ removeEmailAddress: stub })
    wrapper.find('[data-test="btn-remove-passcode-emailAddress-0"').trigger('click')
    expect(wrapper.vm.removeEmailAddress).toBeCalled()
  })
})
