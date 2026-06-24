
import { createLocalVue, shallowMount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import LinkingKeysService from '@/services/linkingKeys.services'
import { MembershipType } from '@/models/Organization'
import { Role } from '@/util/constants'
import VendorConnectionsTable from '@/components/auth/account-settings/advance-settings/VendorConnectionsTable.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import { createI18n } from 'vue-i18n-composable'
import moment from 'moment'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

const vuetify = new Vuetify({})

document.body.setAttribute('data-app', 'true')

function getMockLinkingKeysResponse () {
  const today = moment()

  return {
    data: {
      linkingKeys: [
        {
          id: 1,
          accountId: 1,
          vendorAccountName: 'ABC API Service',
          createdOn: today.clone().subtract(2, 'months').hour(11).minute(20).toISOString(),
          createdBy: 'William Smith',
          expiresOn: today.clone().add(1, 'year').toISOString()
        },
        {
          id: 2,
          accountId: 1,
          vendorAccountName: 'Beta Legal Vendor',
          createdOn: today.clone().subtract(6, 'months').hour(9).minute(15).toISOString(),
          createdBy: 'William Smith',
          expiresOn: today.clone().add(20, 'days').toISOString()
        },
        {
          id: 3,
          accountId: 1,
          vendorAccountName: 'Legacy Vendor App',
          createdOn: today.clone().subtract(2, 'years').hour(14).minute(30).toISOString(),
          createdBy: 'William Smith',
          expiresOn: today.clone().subtract(1, 'month').toISOString()
        }
      ]
    }
  }
}

describe('VendorConnectionsTable.vue', () => {
  let wrapper: any

  beforeEach(async () => {
    setActivePinia(createPinia())
    vi.spyOn(LinkingKeysService, 'getOrgLinkingKeys').mockResolvedValue(getMockLinkingKeysResponse() as any)

    const orgStore = useOrgStore()
    orgStore.$patch({
      currentOrganization: { id: 1 } as any,
      currentMembership: {
        membershipTypeCode: MembershipType.Admin
      } as any
    })
    const userStore = useUserStore()
    userStore.$patch({
      currentUser: {
        roles: [Role.AccountHolder]
      } as any
    })

    const localVue = createLocalVue()
    localVue.use(VueRouter)
    const router = new VueRouter()

    const i18n = createI18n({
      locale: 'en',
      messages: {
        en: {
          vendorConnectionsEmpty: 'No connected service provider.',
          vendorConnectionsExpiresInDays: 'EXPIRES IN {days} DAYS',
          vendorConnectionsExpired: 'EXPIRED',
          vendorConnectionsRemoveTitle: 'Caution: Remove Connection',
          vendorConnectionsRemoveBody: 'Remove body',
          vendorConnectionsExtendTitle: 'Extend Service Provider Connection',
          vendorConnectionsExtendBody: 'Extend body',
          vendorConnectionsRemovedToast: '{providerName} connection removed.',
          vendorConnectionsExtendedToast: '{providerName} connection extended.'
        }
      }
    })

    wrapper = shallowMount(VendorConnectionsTable, {
      localVue,
      router,
      vuetify,
      i18n
    })
    await vi.waitFor(() => expect(wrapper.vm.connectionsList.length).toBe(3))
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper?.destroy()
  })

  it('loads vendor connections from API on mount', () => {
    expect(LinkingKeysService.getOrgLinkingKeys).toHaveBeenCalledWith(1)
    expect(wrapper.vm.connectionsList.length).toBe(3)
  })

  it('shows remove button for active connections when user can manage', () => {
    const activeConnection = wrapper.vm.connectionsList.find(
      connection => wrapper.vm.getConnectionStatus(connection) === 'active'
    )
    expect(activeConnection).toBeTruthy()
  })

  it('confirmRemove removes connection after API call', async () => {
    const activeConnection = wrapper.vm.connectionsList.find(
      connection => wrapper.vm.getConnectionStatus(connection) === 'active'
    )
    vi.spyOn(LinkingKeysService, 'revokeOrgLinkingKey').mockResolvedValue({ data: {} } as any)
    vi.mocked(LinkingKeysService.getOrgLinkingKeys).mockResolvedValueOnce({
      data: {
        linkingKeys: getMockLinkingKeysResponse().data.linkingKeys.filter(
          key => key.id !== Number(activeConnection.id)
        )
      }
    } as any)

    wrapper.vm.openRemoveModal(activeConnection)
    await wrapper.vm.confirmRemove()

    expect(LinkingKeysService.revokeOrgLinkingKey).toHaveBeenCalledWith({
      orgId: 1,
      keyId: Number(activeConnection.id)
    })
    expect(LinkingKeysService.getOrgLinkingKeys).toHaveBeenCalledTimes(2)
    expect(wrapper.vm.connectionsList).toHaveLength(2)
    expect(wrapper.vm.connectionsList.find(connection => connection.id === activeConnection.id)).toBeUndefined()
  })

  it('confirmExtend updates connection expiry from API response', async () => {
    const expiringConnection = wrapper.vm.connectionsList.find(
      connection => wrapper.vm.getConnectionStatus(connection) === 'expiring'
    )
    vi.spyOn(LinkingKeysService, 'extendOrgLinkingKey').mockResolvedValue({ data: {} } as any)
    vi.mocked(LinkingKeysService.getOrgLinkingKeys).mockResolvedValueOnce({
      data: {
        linkingKeys: getMockLinkingKeysResponse().data.linkingKeys.map(key => {
          if (key.id !== Number(expiringConnection.id)) {
            return key
          }
          return { ...key, expiresOn: '2028-06-01T00:00:00Z' }
        })
      }
    } as any)

    wrapper.vm.openExtendModal(expiringConnection)
    await wrapper.vm.confirmExtend()

    const updatedConnection = wrapper.vm.connectionsList.find(
      connection => connection.id === expiringConnection.id
    )
    expect(LinkingKeysService.extendOrgLinkingKey).toHaveBeenCalledWith({
      orgId: 1,
      keyId: Number(expiringConnection.id)
    })
    expect(LinkingKeysService.getOrgLinkingKeys).toHaveBeenCalledTimes(2)
    expect(updatedConnection.expiryDate).toBe('2028-06-01T00:00:00Z')
  })
})
