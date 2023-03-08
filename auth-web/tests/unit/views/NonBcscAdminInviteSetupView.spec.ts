import { createLocalVue, shallowMount } from '@vue/test-utils'

import NonBcscAdminInviteSetupView from '@/views/auth/create-account/non-bcsc/NonBcscAdminInviteSetupView.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)

const vuetify = new Vuetify({})
const router = new VueRouter()

describe('NonBcscAdminInviteSetupView.vue', () => {
  let wrapper: any
  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    const userModule = {
      namespaced: true,
      state: {
        userProfile: {}
      },
      actions: {
        createAffidavit: jest.fn()
      }
    }

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        user: userModule
      }
    })

    wrapper = shallowMount(NonBcscAdminInviteSetupView, {
      store,
      localVue,
      router,
      vuetify
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

  it('update current step properly', async () => {
    wrapper.vm.goToNextStep()
    expect(wrapper.vm.currentStep).toEqual(2)
    wrapper.vm.goBackPreviousStep()
    expect(wrapper.vm.currentStep).toEqual(1)
  })
})
