import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import BusinessProfileView from '@/views/auth/BusinessProfileView.vue'

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

    wrapper = mount(BusinessProfileView, {
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
