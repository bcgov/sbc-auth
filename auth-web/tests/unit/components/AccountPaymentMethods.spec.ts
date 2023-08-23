import { createLocalVue, shallowMount } from '@vue/test-utils'
import { useBusinessStore, useOrgStore, useUserStore } from '@/store'
import AccountPaymentMethods from '@/components/auth/account-settings/payment/AccountPaymentMethods.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})

// Prevent error redundant navigation.
const originalPush = VueRouter.prototype.push
VueRouter.prototype.push = function push (location) {
  return originalPush.call(this, location).catch(() => {})
}

describe('AccountPaymentMethods.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(VueRouter)

    const router = new VueRouter()
    const orgStore = useOrgStore()
    orgStore.currentOrganization = {
      name: 'new org',
      orgType: 'STAFF'
    }
    const businessStore = useBusinessStore()
    businessStore.businesses = []
    const userStore = useUserStore()
    userStore.currentUser = {
      firstName: 'test',
      lastName: 'test'
    } as any
    wrapperFactory = (propsData) => {
      return shallowMount(AccountPaymentMethods, {
        localVue,
        router,
        vuetify,
        propsData: {
          ...propsData
        }
      })
    }

    wrapper = wrapperFactory({})
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
  })

  afterAll(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the components properly and address is being shown', () => {
    expect(wrapper.findComponent(AccountPaymentMethods).exists()).toBe(true)
  })

  it('renders proper header content', () => {
    expect(wrapper.find('h2').text()).toBe('Payment Methods')
  })

  it('renders sub text content', () => {
    expect(wrapper.find('p').text()).toBe('Manage your payment method for this account.')
  })
})
