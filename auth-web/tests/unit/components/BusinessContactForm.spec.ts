import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import BusinessContactForm from '@/components/auth/BusinessContactForm.vue'
import { useBusinessStore } from '@/stores/business'

describe('BusinessContactForm.vue', () => {
  let wrapper: Wrapper<BusinessContactForm>
  const config = {
    'AUTH_API_URL': 'https://localhost:8080/api/v1/11',
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()

    const businessStore = useBusinessStore()
    businessStore.currentBusiness = {
      businessIdentifier: 'CP0000000',
      businessNumber: 'CP0000000',
      contacts: [
        {
          created: '2019-12-11T04:03:11.830365+00:00',
          createdBy: 'TEST',
          email: 'test@gmail.com',
          modified: '2019-12-11T04:03:11.830395+00:00',
          phone: '',
          phoneExtension: ''
        }
      ],
      folioNumber: '22222222222'
    } as any

    wrapper = mount(BusinessContactForm, {
      localVue
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

  it('business contact form has save and skip buttons', () => {
    expect(wrapper.find('.save-continue-button')).toBeTruthy()
    expect(wrapper.find('.skip-button')).toBeTruthy()
  })

  it('email data is test@gmail.com', () => {
    expect(wrapper.vm.$data.emailAddress).toBe('test@gmail.com')
  })

  it('confirm email data is test@gmail.com', () => {
    expect(wrapper.vm.$data.confirmedEmailAddress).toBe('test@gmail.com')
  })

  it('confirm phone data is empty', () => {
    expect(wrapper.vm.$data.phoneNumber).toBe('')
  })

  it('confirm extension data to be empty', () => {
    expect(wrapper.vm.$data.extension).toBe('')
  })
})
