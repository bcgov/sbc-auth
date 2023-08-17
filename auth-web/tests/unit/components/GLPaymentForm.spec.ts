import { createLocalVue, mount } from '@vue/test-utils'
import GLPaymentForm from '@/components/auth/common/GLPaymentForm.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)

describe('GLPaymentForm.vue', () => {
  let wrapper: any
  const config = {
    'AUTH_API_URL': 'https://localhost:8080/api/v1/11',
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

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
        setCurrentOrganizationGLInfo: vi.fn()
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

    vi.resetModules()
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })
})
