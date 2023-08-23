import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import SetupAccountForm from '@/components/auth/staff/SetupAccountForm.vue'
import Vuetify from 'vuetify'
import { useStaffStore } from '@/store'

describe('SetupAccountForm.vue', () => {
  let wrapper: Wrapper<SetupAccountForm>
  const config = {
    'AUTH_API_URL': 'https://localhost:8080/api/v1/11',
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()

    const staffStore = useStaffStore()
    staffStore.products = [
      {
        'code': 'PPR',
        'default': false,
        'desc': 'Personal Property Registry'
      },
      {
        'code': 'DIR_SEARCH',
        'default': false,
        'desc': 'Director Search'
      }
    ]
    staffStore.accountTypes = [
      {
        'code': 'IMPLICIT',
        'default': true,
        'desc': 'Implicit organization for internal user only'
      },
      {
        'code': 'EXPLICIT',
        'default': false,
        'desc': 'Explicity named organization that can have multiple members'
      },
      {
        'code': 'PUBLIC',
        'default': false,
        'desc': 'PUBLIC'
      }
    ]
    const vuetify = new Vuetify({})

    wrapper = mount(SetupAccountForm, {
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

  it('business contact form has submit and cancel buttons', () => {
    expect(wrapper.find('.submit-form-btn')).toBeTruthy()
    expect(wrapper.find('.cancel-btn')).toBeTruthy()
  })

  it('confirm account name is empty', () => {
    expect(wrapper.vm.$data.accountName).toBe('')
  })

  it('confirm email to be empty', () => {
    expect(wrapper.vm.$data.email).toBe('')
  })
})
