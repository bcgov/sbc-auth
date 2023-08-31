import { createLocalVue, mount } from '@vue/test-utils'
import { useBusinessStore, useOrgStore, useUserStore } from '@/stores'
import PendingMemberDataTable from '@/components/auth/account-settings/team-management/PendingMemberDataTable.vue'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})

vi.mock('../../../src/services/bcol.services')

describe('PendingMemberDataTable.vue', () => {
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
    orgStore.currentOrganization = {} as any
    orgStore.pendingOrgInvitations = []
    orgStore.activeOrgMembers = [{ 'membershipTypeCode': 'OWNER', 'user': { 'username': 'test' } }] as any
    orgStore.pendingOrgMembers = [{ 'membershipTypeCode': 'OWNER', 'user': { 'username': 'test' } }] as any
    const userStore = useUserStore()
    userStore.currentUser = { 'userName': 'test' } as any
    const businessStore = useBusinessStore()
    businessStore.businesses = []

    vi.resetModules()
    vi.clearAllMocks()
  })

  it('Mounting works', () => {
    const $t = () => 'test'
    const wrapper = mount(PendingMemberDataTable, {
      store,
      vuetify,
      localVue,
      mocks: { $t }
    })
    expect(wrapper.find('.user-list')).toBeTruthy()
    wrapper.destroy()
  })
})
