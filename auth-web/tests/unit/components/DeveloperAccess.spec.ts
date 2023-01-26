
import { createLocalVue, shallowMount } from '@vue/test-utils'
import DeveloperAccess from '@/components/auth/account-settings/advance-settings/DeveloperAccess.vue'
import ExistingAPIKeys from '@/components/auth/account-settings/advance-settings/ExistingAPIKeys.vue'

import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('GovmPaymentMethodSelector.vue', () => {
  let wrapper: any
  let wrapperFactory: any
  const config = {
    'AUTH_API_URL': 'https://localhost:8080/api/v1/11',
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1',
    'API_DOCUMENTATION_URL': 'https://developer.bcregistry.daxiom.ca/'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(VueRouter)
    const router = new VueRouter()

    const store = new Vuex.Store({
      strict: false,
      modules: {}
    })
    const $t = () => 'test trans data'

    wrapperFactory = (propsData) => {
      return shallowMount(DeveloperAccess, {
        localVue,
        store,
        router,
        vuetify,
        mocks: { $t },
        propsData: {
          ...propsData
        }
      })
    }

    wrapper = wrapperFactory({ userProfile: {} })
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('renders the components properly and DeveloperAccess should be  shown', () => {
    expect(wrapper.find(ExistingAPIKeys).exists()).toBe(true)
    expect(wrapper.find('h2').text()).toBe('Developer Access')
  })
})
