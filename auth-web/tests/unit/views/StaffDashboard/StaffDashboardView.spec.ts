import { LDFlags, Role } from '@/util/constants'
import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import { useCodesStore, useOrgStore, useStaffStore, useTaskStore, useUserStore } from '@/stores'
import { BaseVExpansionPanel } from '@/components'
import ConfigHelper from '@/util/config-helper'
import ContinuationApplications from '@/components/auth/staff/continuation-application/ContinuationApplications.vue'
import GLCodesListView from '@/views/auth/staff/GLCodesListView.vue'
import IncorporationSearchResultView from '@/views/auth/staff/IncorporationSearchResultView.vue'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import LaunchTile from '@/components/LaunchTile.vue'
import { MembershipType } from '@/models/Organization'
import PPRLauncher from '@/components/auth/staff/PPRLauncher.vue'
import StaffAccountManagement from '@/components/auth/staff/account-management/StaffAccountManagement.vue'
import StaffDashboardView from '@/views/auth/staff/StaffDashboardView.vue'
import { Transactions } from '@/components/auth/account-settings/transaction'
import Vue from 'vue'
import Vuetify from 'vuetify'
import { createI18n } from 'vue-i18n-composable'
import { staffPermissions } from '../../test-utils/test-data/permissions'

const vuetify = new Vuetify({})

describe('StaffDashboardView tests', () => {
  let wrapper: Wrapper<any>
  let i18n: any

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
    orgStore.syncStaffPermissions = vi.fn().mockResolvedValue(staffPermissions)

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

    i18n = createI18n({
      locale: 'en',
      messages: {
        en: {
          viewAllProductsLauncherTitle: 'View All Products',
          viewAllProductsLauncherText: 'Click here to view all products'
        }
      }
    })

    wrapper = mount(StaffDashboardView, {
      localVue,
      vuetify,
      i18n,
      stubs: ['Transactions', 'StaffAccountManagement', 'ContinuationApplications', 'PPRLauncher', 'GLCodesListView']
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
    expect(wrapper.findComponent(ContinuationApplications).exists()).toBe(true)
    expect(wrapper.find('#EFT-button').exists())
    expect(wrapper.find('#FAS-button').exists())
    expect(wrapper.find('#involuntary-dissolution-button').exists())
    const expansionPanels = wrapper.findAll(BaseVExpansionPanel)
    expect(expansionPanels.length).toBe(3)
    // hidden by closed BaseVExpansionPanel
    expect(wrapper.findComponent(GLCodesListView).exists()).toBe(false)
    expect(wrapper.findComponent(Transactions).exists()).toBe(false)
    // expanding shows it
    expansionPanels.at(0).find('button').trigger('click')
    await Vue.nextTick()
    expect(wrapper.findComponent(GLCodesListView).exists()).toBe(true)
    expansionPanels.at(1).find('button').trigger('click')
    await Vue.nextTick()
    expect(wrapper.findComponent(Transactions).exists()).toBe(true)
  })

  const mountWithFlags = (payInsightsOn: boolean) => {
    vi.spyOn(LaunchDarklyService, 'getFlag').mockImplementation(
      (flag: string) => flag === LDFlags.EnablePayInsights ? payInsightsOn : false
    )
    return mount(StaffDashboardView, {
      localVue: createLocalVue(),
      vuetify,
      i18n,
      stubs: ['Transactions', 'StaffAccountManagement', 'ContinuationApplications', 'PPRLauncher', 'GLCodesListView']
    })
  }

  const payInsightsTile = () => wrapper.findAllComponents(LaunchTile)
    .wrappers.find(t => t.props('tileConfig').title === 'PAY Insights')

  it('shows the PAY Insights tile for staff when the flag is on', () => {
    wrapper = mountWithFlags(true)
    const tile = payInsightsTile().props('tileConfig')
    expect(tile.showTile).toBe(true)
    expect(tile.href).toBe(ConfigHelper.getPayInsightsUrl())
  })

  it('hides the PAY Insights tile when the flag is off', () => {
    wrapper = mountWithFlags(false)
    expect(payInsightsTile().props('tileConfig').showTile).toBe(false)
  })

  it('hides the PAY Insights tile without the staff role, even with the flag on', () => {
    useUserStore().currentUser = { roles: [Role.FasSearch] } as any
    wrapper = mountWithFlags(true)
    expect(payInsightsTile().props('tileConfig').showTile).toBe(false)
  })
})
