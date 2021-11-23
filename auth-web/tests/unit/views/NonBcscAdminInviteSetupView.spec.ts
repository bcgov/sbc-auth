import { createLocalVue, shallowMount } from '@vue/test-utils'

import NonBcscAdminInviteSetupView from '@/views/auth/create-account/non-bcsc/NonBcscAdminInviteSetupView.vue'
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

describe('NonBcscAdminInviteSetupView.vue', () => {
  let wrapper: any

  beforeEach(() => {
    sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockSession)
    const localVue = createLocalVue()
    localVue.use(Vuex)

    wrapper = shallowMount(NonBcscAdminInviteSetupView, {
      localVue,
      router,
      vuetify
    })
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('update current step properly', async () => {
    wrapper.vm.goToNextStep()
    expect(wrapper.vm.currentStep).toEqual(2)
    wrapper.vm.goBackPreviousStep()
    expect(wrapper.vm.currentStep).toEqual(1)
  })
})
