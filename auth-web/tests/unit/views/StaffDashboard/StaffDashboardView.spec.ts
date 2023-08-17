import '../../test-utils/composition-api-setup' // important to import this first
import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
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
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(Vuex)

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('StaffDashboardView tests', () => {
  let wrapper: Wrapper<any>
  let sandbox: any

  const config = {
    AUTH_API_URL: 'https://localhost:8080/api/v1/app',
    PAY_API_URL: 'https://pay-api.gov.bc.ca/api/v1'
  }
  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(async () => {
    const localVue = createLocalVue()
    // store
    const orgModule = {
      namespaced: true,
      state: {
        currentOrgPaymentDetails: { accountId: 123 },
        currentOrganization: { id: 123 },
        currentMembership: { membershipTypeCode: MembershipType.Admin }
      },
      actions: { getOrgPayments: vi.fn(() => { return { credit: 0 } }) }
    }
    const userModule = {
      namespaced: true,
      state: {
        currentUser: {
          roles: [Role.FasSearch, Role.Staff, Role.ViewAllTransactions, Role.StaffViewAccounts, Role.ManageGlCodes]
        }
      }
    }
    const codeModule = {
      namespaced: true,
      state: {},
      actions: { getCodes: vi.fn(() => []) }
    }
    const taskModule = {
      namespaced: true,
      state: { pendingTasksCount: 0, rejectedTasksCount: 0 },
      actions: { syncTasks: vi.fn() }
    }
    const staffModule = {
      namespaced: true,
      state: {
        pendingInvitationsCount: 0,
        suspendedReviewCount: 0
      },
      actions: {
        syncPendingInvitationOrgs: vi.fn(() => []),
        syncSuspendedStaffOrgs: vi.fn(() => [])
      }
    }

    const store = new Vuex.Store({
      strict: false,
      modules: { org: orgModule, user: userModule, code: codeModule, task: taskModule, staff: staffModule }
    })

    wrapper = mount(StaffDashboardView, {
      localVue,
      vuetify,
      store,
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
