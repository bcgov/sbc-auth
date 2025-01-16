import '../test-utils/composition-api-setup' // important to import this first
import { AccountStatus, PaymentTypes, Role } from '@/util/constants'
import { createLocalVue, mount } from '@vue/test-utils'
import { useOrgStore, useUserStore } from '@/stores'
import AccountFreezeUnlockView from '@/views/auth/account-freeze/AccountFreezeUnlockView.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'

const localVue = createLocalVue()
const vuetify = new Vuetify({})
const router = new VueRouter()
localVue.use(Vuetify)
localVue.use(VueRouter)

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('AccountFreezeUnlockView', () => {
  let wrapper: any

  beforeEach(() => {
    const orgStore = useOrgStore()
    const userStore = useUserStore()

    orgStore.currentOrganization = {
      statusCode: AccountStatus.NSF_SUSPENDED
    } as any

    userStore.currentUser = {
      firstName: 'Fred',
      lastName: 'Flinstone',
      roles: [Role.Staff]
    } as any

    wrapper = mount(AccountFreezeUnlockView, {
      localVue,
      router,
      vuetify,
      mocks: {
        $t: (mock) => mock
      }
    })
    wrapper.vm.isViewLoading = false
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('Should be a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('Should have error dialog', () => {
    expect(wrapper.find({ ref: 'errorDialog' }).exists()).toBe(true)
  })

  it('Should not render view if not loaded', async () => {
    wrapper.vm.isViewLoading = true
    await wrapper.vm.$nextTick()
    expect(wrapper.find('h1').exists()).toBe(false)
  })

  it('Should render NSF view', async () => {
    wrapper.vm.isAccountStatusNsfSuspended = true
    await wrapper.vm.$nextTick()
    expect(wrapper.find('h1').text()).toBe('Your Account is Suspended')
    expect(wrapper.find('p').text()).toBe('Important:  Please complete the following steps to complete your payment.')
  })

  it('Should render <Stepper>', () => {
    expect(wrapper.findComponent({ name: 'stepper' }).exists()).toBe(true)
  })
})

describe('AccountFreezeUnlockView (EFT)', () => {
  let wrapper: any

  beforeEach(() => {
    const orgStore = useOrgStore()
    const userStore = useUserStore()

    orgStore.currentOrganization = {
      statusCode: AccountStatus.NSF_SUSPENDED
    } as any

    orgStore.calculateFailedInvoices = vi.fn(() => ({
      totalTransactionAmount: 10,
      totalAmountToPay: 20
    })) as any

    orgStore.getOrgPayments = vi.fn().mockReturnValue({ paymentMethod: PaymentTypes.EFT })

    userStore.currentUser = {
      firstName: 'Fred',
      lastName: 'Flinstone',
      roles: [Role.Staff]
    } as any

    wrapper = mount(AccountFreezeUnlockView, {
      localVue,
      router,
      vuetify,
      mocks: {
        $t: (mock) => mock
      }
    })
    wrapper.vm.isViewLoading = false
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('Should render NSF EFT view', async () => {
    wrapper.vm.isAccountStatusNsfSuspended = true
    await flushPromises()
    expect(wrapper.find('h1').text()).toBe('Your Account is Suspended')
    expect(wrapper.vm.stepperConfig.length).toBe(2)
  })

  it('Should render <Stepper>', () => {
    expect(wrapper.findComponent({ name: 'stepper' }).exists()).toBe(true)
  })
})
