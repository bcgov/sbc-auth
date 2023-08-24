
import { createLocalVue, shallowMount } from '@vue/test-utils'
import DeveloperAccess from '@/components/auth/account-settings/advance-settings/DeveloperAccess.vue'
import ExistingAPIKeys from '@/components/auth/account-settings/advance-settings/ExistingAPIKeys.vue'

import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('DeveloperAccess.vue', () => {
  let wrapper: any
  let wrapperFactory: any
  const config = {
    'AUTH_API_URL': 'https://localhost:8080/api/v1/11',
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1',
    'API_DOCUMENTATION_URL': 'https://developer.bcregistry.daxiom.ca/'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    const router = new VueRouter()

    const $t = () => 'test trans data'

    wrapperFactory = (propsData) => {
      return shallowMount(DeveloperAccess, {
        localVue,
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
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the components properly and DeveloperAccess should be  shown', () => {
    expect(wrapper.findComponent(ExistingAPIKeys).exists()).toBe(true)
    expect(wrapper.find('h2').text()).toBe('Developer Access')
  })
})
