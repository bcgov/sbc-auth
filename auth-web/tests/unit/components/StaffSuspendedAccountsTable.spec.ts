import { Wrapper, createLocalVue, shallowMount } from '@vue/test-utils'
import StaffSuspendedAccountsTable from '@/components/auth/staff/account-management/StaffSuspendedAccountsTable.vue'
import Vuetify from 'vuetify'
import { useStaffStore } from '@/stores/staff'

describe('StaffSuspendedAccountsTable.vue', () => {
  let wrapper: Wrapper<StaffSuspendedAccountsTable>

  beforeEach(() => {
    const localVue = createLocalVue()

    const staffStore = useStaffStore()
    staffStore.suspendedStaffOrgs = [
      {
        'modified': '2020-12-10T21:05:06.144977+00:00',
        'name': 'NEW BC ONLINE TECH TEAM',
        'orgType': 'PREMIUM',
        'orgStatus': 'NSF_SUSPENDED',
        'products': [
          2342,
          2991
        ],
        'statusCode': 'NSF_SUSPENDED',
        'suspendedOn': '2020-12-01T17:52:03.747200+00:00'
      }
    ] as any

    const $t = () => ''
    wrapper = shallowMount(StaffSuspendedAccountsTable, {
      localVue,
      vuetify: new Vuetify({}),
      mocks: { $t }
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

  it('Should have data table', () => {
    expect(wrapper.find('.account-list')).toBeTruthy()
  })
})
