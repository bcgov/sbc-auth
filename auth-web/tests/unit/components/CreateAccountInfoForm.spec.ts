import { createLocalVue, shallowMount } from '@vue/test-utils'
import CreateAccountInfoForm from '@/components/auth/create-account/CreateAccountInfoForm.vue'
import { useOrgStore } from '@/stores/org'

vi.mock('../../../src/services/bcol.services')

describe('CreateAccountInfoForm.vue', () => {
  let localVue
  let store

  const config = {
    AUTH_API_URL: 'https://localhost:8080/api/v1/11',
    PAY_API_URL: 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)
  beforeEach(() => {
    localVue = createLocalVue()
    const orgStore = useOrgStore()
    orgStore.currentOrganization = {
      orgType: 'PREMIUM'
    } as any
    vi.resetModules()
    vi.clearAllMocks()
  })

  it('Mounting works', () => {
    const $t = () => 'test'
    const wrapper = shallowMount(CreateAccountInfoForm, {
      store,
      localVue,
      mocks: { $t }
    })
    expect(wrapper.find('.user-list')).toBeTruthy()
    wrapper.destroy()
  })
})
