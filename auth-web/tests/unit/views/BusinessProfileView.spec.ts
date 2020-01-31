import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import BusinessContactForm from '@/components/auth/BusinessContactForm.vue'
import BusinessModule from '@/store/modules/business'
import BusinessProfileView from '@/views/auth/BusinessProfileView.vue'
import SupportInfoCard from '@/components/SupportInfoCard.vue'

import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)

jest.mock('axios', () => ({
  post: jest.fn(() => Promise.resolve({ data: { access_token: 'abcd', refresh_token: 'efgh', registries_trace_id: '12345abcde' } }))
}))

describe('BusinessProfileView.vue', () => {
  let wrapper: Wrapper<BusinessProfileView>
  var ob = {
    'VUE_APP_COPS_REDIRECT_URL': 'http://localhost:8081',
    'VUE_APP_PAY_ROOT_API': 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1',
    'VUE_APP_AUTH_ROOT_API': 'https://auth-api-post-dev.pathfinder.gov.bc.ca/api/v1',
    'VUE_APP_LEGAL_ROOT_API': 'https://legal-api-dev.pathfinder.gov.bc.ca/api/v1',
    'VUE_APP_FLAVOR': 'post-mvp'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(ob)
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
        loadBusiness: jest.fn()
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

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })
})
