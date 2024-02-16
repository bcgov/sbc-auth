import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import { useCodesStore, useOrgStore, useStaffStore, useTaskStore, useUserStore } from '@/stores'
import { BaseVExpansionPanel } from '@/components'
import GLCodesListView from '@/views/auth/staff/GLCodesListView.vue'
import IncorporationSearchResultView from '@/views/auth/staff/IncorporationSearchResultView.vue'
import { MembershipType } from '@/models/Organization'
import PPRLauncher from '@/components/auth/staff/PPRLauncher.vue'
import { Role } from '@/util/constants'
import StaffAccountManagement from '@/components/auth/staff/account-management/StaffAccountManagement.vue'
import StaffDashboardView from '@/views/auth/staff/StaffDashboardView.vue'
import { Transactions } from '@/components/auth/account-settings/transaction'
import Vue from 'vue'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})

describe('StaffDashboardView tests', () => {
  let wrapper: Wrapper<any>

  const config = {
    AUTH_API_URL: 'https://localhost:8080/api/v1/app',
    PAY_API_URL: 'https://pay-api.gov.bc.ca/api/v1'
  }
  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(async () => {
    const localVue = createLocalVue()
    const orgStore = useOrgStore()
    orgStore.currentOrgPaymentDetails = { accountId: 123 } as any
    orgStore.currentOrganization = { id: 123 } as any
    orgStore.currentMembership = { membershipTypeCode: MembershipType.Admin } as any

    const userStore = useUserStore()
    userStore.currentUser = {
      roles: [Role.FasSearch, Role.Staff, Role.ViewAllTransactions, Role.StaffViewAccounts, Role.ManageGlCodes, Role.ManageEft]
    } as any

    const codeStore = useCodesStore()
    codeStore.getCodes = vi.fn(() => []) as any

    const taskStore = useTaskStore()
    taskStore.pendingTasksCount = 0
    taskStore.rejectedTasksCount = 0

    const staffStore = useStaffStore()
    staffStore.pendingInvitationOrgs = []
    staffStore.suspendedStaffOrgs = []

    wrapper = mount(StaffDashboardView, {
      localVue,
      vuetify,
      stubs: ['Transactions', 'StaffAccountManagement', 'PPRLauncher', 'GLCodesListView']
    })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders view with child components', async () => {
    expect(wrapper.findComponent(StaffDashboardView).exists()).toBe(true)
    expect(wrapper.find('.view-header__title').text()).toBe('Staff Dashboard')
    expect(wrapper.findComponent(PPRLauncher).exists()).toBe(true)
    expect(wrapper.findComponent(IncorporationSearchResultView).exists()).toBe(true)
    expect(wrapper.findComponent(StaffAccountManagement).exists()).toBe(true)
    expect(wrapper.findComponent(GLCodesListView).exists()).toBe(true)
    expect(wrapper.find('#EFT-button').exists())
    const expansionPanels = wrapper.findAll(BaseVExpansionPanel)
    expect(expansionPanels.length).toBe(3)
    // hidden by closed BaseVExpansionPanel
    expect(wrapper.findComponent(Transactions).exists()).toBe(false)
    // expanding shows it
    expansionPanels.at(0).find('button').trigger('click')
    await Vue.nextTick()
    expect(wrapper.findComponent(Transactions).exists()).toBe(true)
  })
})
