
import { createLocalVue, shallowMount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import { MembershipType } from '@/models/Organization'
import { Role } from '@/util/constants'
import VendorConnections from '@/components/auth/account-settings/advance-settings/VendorConnections.vue'
import VendorConnectionsTable from '@/components/auth/account-settings/advance-settings/VendorConnectionsTable.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

const vuetify = new Vuetify({})

document.body.setAttribute('data-app', 'true')

describe('VendorConnections.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.spyOn(LaunchDarklyService, 'getFlag').mockReturnValue(false)

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

    const $t = (key: string) => key

    wrapperFactory = () => {
      return shallowMount(VendorConnections, {
        localVue,
        router,
        vuetify,
        mocks: { $t }
      })
    }

    wrapper = wrapperFactory()
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    vi.restoreAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders VendorConnectionsTable', () => {
    expect(wrapper.findComponent(VendorConnectionsTable).exists()).toBe(true)
  })

  it('renders the page title translation key', () => {
    expect(wrapper.find('[data-test="vendor-connections-title"]').text()).toBe('vendorConnectionsTitle')
  })
})
