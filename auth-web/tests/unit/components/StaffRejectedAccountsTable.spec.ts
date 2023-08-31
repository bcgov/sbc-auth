import { Wrapper, createLocalVue, shallowMount } from '@vue/test-utils'
import StaffRejectedAccountsTable from '@/components/auth/staff/account-management/StaffRejectedAccountsTable.vue'
import Vuetify from 'vuetify'
import { useStaffStore } from '@/stores/staff'

describe('StaffRejectedAccountsTable.vue', () => {
  let wrapper: Wrapper<StaffRejectedAccountsTable>

  beforeEach(() => {
    const localVue = createLocalVue()

    const staffStore = useStaffStore()
    staffStore.rejectedStaffOrgs = [
      {
        'modified': '2020-12-10T22:05:06.144977+00:00',
        'name': 'NEW BC ONLINE TECH TEAM',
        'orgType': 'BASIC',
        'orgStatus': 'ACTIVE',
        'products': [
          2341,
          2992
        ],
        'statusCode': 'ACTIVE'
      }
    ] as any

    const vuetify = new Vuetify({})

    const $t = () => ''
    wrapper = shallowMount(StaffRejectedAccountsTable, {
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

  it('is a Vue instance and has a data table', () => {
    expect(wrapper.vm).toBeTruthy()
    expect(wrapper.find('.user-list')).toBeTruthy()
  })
})
