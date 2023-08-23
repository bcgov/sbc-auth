import { createLocalVue, mount } from '@vue/test-utils'
import AccountOverview from '@/components/auth/account-freeze/AccountOverview.vue'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import Vuetify from 'vuetify'
import { useOrgStore } from '@/store'

describe('AccountOverview.vue', () => {
  let wrapper: any
  const config = {
    'AUTH_API_URL': 'https://localhost:8080/api/v1/11',
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()

    const vuetify = new Vuetify({})

    const orgStore = useOrgStore()
    orgStore.currentOrganization = { id: 5 } as any

    wrapper = mount(AccountOverview, {
      localVue,
      vuetify,
      mixins: [Steppable]
    })

    vi.resetModules()
    vi.clearAllMocks()
  })

  afterAll(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('should render info card', () => {
    expect(wrapper.find('.suspended-info-card')).toBeTruthy()
  })

  it('should render download button', () => {
    expect(wrapper.find('.download-pdf-btn')).toBeTruthy()
  })

  it('should render next button', () => {
    expect(wrapper.find('.v-btn').text('Next')).toBeTruthy()
  })
})
