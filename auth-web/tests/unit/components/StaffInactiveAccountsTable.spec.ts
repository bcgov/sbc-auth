import { createLocalVue, shallowMount } from '@vue/test-utils'
import StaffInactiveAccountsTable from '@/components/auth/staff/account-management/StaffInactiveAccountsTable.vue'
import Vuetify from 'vuetify'
import { useStaffStore } from '@/stores'

describe('StaffInactiveAccountsTable.vue', () => {
  let wrapper: any

  const config = {
    'AUTH_API_URL': 'https://localhost:8080/api/v1/11',
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()

    const staffStore = useStaffStore()
    staffStore.suspendedStaffOrgs = [
      {
        'modified': '2020-12-10T21:05:06.144977+00:00',
        'name': 'NEW BC ONLINE TECH TEAM',
        'orgType': 'PREMIUM',
        'orgStatus': 'ACTIVE',
        'products': [
          2342,
          2991
        ],
        'statusCode': 'ACTIVE',
        'suspendedOn': '2020-12-01T17:52:03.747200+00:00'
      }
    ] as any

    const vuetify = new Vuetify({})

    const $t = () => ''
    wrapper = shallowMount(StaffInactiveAccountsTable, {
      localVue,
      vuetify,
      mocks: { $t }
    })

    vi.resetModules()
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })
  // TOFIX fix orgs undefiend
  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('Should have data table', () => {
    expect(wrapper.find('.account-list')).toBeTruthy()
  })
})
