
import { createLocalVue, shallowMount } from '@vue/test-utils'
import DeveloperAccess from '@/components/auth/account-settings/advance-settings/DeveloperAccess.vue'
import ExistingAPIKeys from '@/components/auth/account-settings/advance-settings/ExistingAPIKeys.vue'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'

import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import { useOrgStore } from '@/stores/org'

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

    const $t = vi.fn(() => 'test trans data')

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

  it.each([
    [false, 'prod', 'developerAccessSubtitle'],
    [true, '', 'developerAccessSubtitle'],
    [true, 'sandbox', 'developerAccessSubtitleSandbox'],
    [true, 'prod', 'developerAccessSubtitleProd']
  ])('with EnableCreateApiKey %s and environment "%s" uses %s', (flag, environment, key) => {
    vi.spyOn(LaunchDarklyService, 'getFlag').mockReturnValue(flag)
    useOrgStore().apiKeysEnvironment = environment as any
    wrapper.destroy()
    wrapper = wrapperFactory({})
    expect(wrapper.vm.$t).toHaveBeenLastCalledWith(key, expect.anything())
  })
})
