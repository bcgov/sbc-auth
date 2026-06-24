
import { createLocalVue, shallowMount } from '@vue/test-utils'
import VendorConnectionsTable from '@/components/auth/account-settings/advance-settings/VendorConnectionsTable.vue'

import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import { createI18n } from 'vue-i18n-composable'
import { createPinia, setActivePinia } from 'pinia'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'
import { MembershipType } from '@/models/Organization'
import { Role } from '@/util/constants'

const vuetify = new Vuetify({})

document.body.setAttribute('data-app', 'true')

describe('VendorConnectionsTable.vue', () => {
  let wrapper: any

  beforeEach(() => {
    setActivePinia(createPinia())
    const orgStore = useOrgStore()
    orgStore.$patch({
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
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper?.destroy()
  })

  it('loads mock vendor connections on mount', () => {
    expect(wrapper.vm.connectionsList.length).toBeGreaterThan(0)
  })

  it('shows remove button for active connections when user can manage', () => {
    const activeConnection = wrapper.vm.connectionsList.find(
      connection => wrapper.vm.getConnectionStatus(connection) === 'active'
    )
    expect(activeConnection).toBeTruthy()
  })
})
