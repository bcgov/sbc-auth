import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import BusinessProfileView from '@/views/auth/BusinessProfileView.vue'

import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('BusinessProfileView.vue', () => {
  let wrapper: Wrapper<BusinessProfileView>
  const ob = {
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1',
    'AUTH_API_URL': 'https://auth-api-post-dev.pathfinder.gov.bc.ca/api/v1',
    'LEGAL_API_URL': 'https://legal-api-dev.pathfinder.gov.bc.ca/api/v1',
    'VUE_APP_FLAVOR': 'post-mvp'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(ob)
  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const businessModule = {
      namespaced: true,
      state: {
        currentBusiness: {
        }
      },
      actions: {
        loadBusiness: vi.fn()
      }
    }
    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        business: businessModule
      }
    })

    wrapper = mount(BusinessProfileView, {
      store,
      localVue,
      stubs: {
        BusinessContactForm: true,
        SupportInfoCard: true
      }
    })

    vi.resetModules()
    vi.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })
})
