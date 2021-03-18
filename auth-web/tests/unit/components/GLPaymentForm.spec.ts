import { createLocalVue, mount } from '@vue/test-utils'
import { Account } from '@/util/constants'
import GLPaymentForm from '@/components/auth/common/GLPaymentForm.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)

describe('GLPaymentForm.vue', () => {
  let wrapper: any
  const config = {
    'VUE_APP_ROOT_API': 'https://localhost:8080/api/v1/11',
    'VUE_APP_COPS_REDIRECT_URL': 'https://coops-dev.pathfinder.gov.bc.ca/',
    'VUE_APP_PAY_ROOT_API': 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const vuetify = new Vuetify({})

    const orgModule = {
      namespaced: true,
      state: {
        currentOrgGLInfo: {
          'clientCode': '123',
          'responsiblityCenter': '123',
          'accountNumber': '12345',
          'standardObject': '1234',
          'project': '1234'
        }
      },
      actions: {},
      mutations: {
        setCurrentOrganizationGLInfo: jest.fn()
      },
      getters: {}
    }
    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        org: orgModule
      }
    })

    wrapper = mount(GLPaymentForm, {
      store,
      localVue,
      vuetify
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })
})
