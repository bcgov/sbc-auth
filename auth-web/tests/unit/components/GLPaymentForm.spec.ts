import { createLocalVue, mount } from '@vue/test-utils'
import GLPaymentForm from '@/components/auth/common/GLPaymentForm.vue'
import Vuetify from 'vuetify'
import { useOrgStore } from '@/stores/org'

describe('GLPaymentForm.vue', () => {
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
    orgStore.currentOrgGLInfo = {
      'clientCode': '123',
      'responsiblityCenter': '123',
      'accountNumber': '12345',
      'standardObject': '1234',
      'project': '1234'
    } as any

    wrapper = mount(GLPaymentForm, {
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
