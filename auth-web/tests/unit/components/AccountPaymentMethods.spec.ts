import { createLocalVue, shallowMount } from '@vue/test-utils'
import { useBusinessStore, useOrgStore, useUserStore } from '@/stores'
import AccountPaymentMethods from '@/components/auth/account-settings/payment/AccountPaymentMethods.vue'
import { LoginSource, PaymentTypes } from '@/util/constants'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

vi.mock('@/composables/product-payment-factory', () => ({
  useProductPayment: () => ({
    hasProductOrPaymentBackendChanges: vi.fn().mockResolvedValue(false)
  })
}))

const vuetify = new Vuetify({})

vi.mock('../../../src/services/user.services')
vi.mock('../../../src/services/org.services')

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
    orgStore.syncAddress = () => {
      return Promise.resolve()
    }
    orgStore.getOrgProducts = () => {
      return Promise.resolve([])
    }
    orgStore.getOrgPayments = () => {
      return Promise.resolve([]) as any
    }
    const businessStore = useBusinessStore()
    businessStore.businesses = []
    const userStore = useUserStore()
    userStore.currentUser = {
      firstName: 'test',
      lastName: 'test',
      loginSource: LoginSource.BCSC
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

  it('sets errorText and errorTitle correctly for a 400 BCOL error response', async () => {
    const orgStore = useOrgStore()

    orgStore.updateOrg = vi.fn().mockRejectedValue({
      response: {
        status: 400,
        data: {
          code: 'BCOL API Error',
          detail: null,
          message: {
            detail: 'Invalid User ID or Password',
            title: 'Invalid Credentials',
            type: 'INVALID_CREDENTIALS'
          }
        }
      }
    })

    // Set up component state so save() proceeds past validation
    wrapper.vm.selectedPaymentMethod = PaymentTypes.CREDIT_CARD
    wrapper.vm.isBtnSaved = false
    wrapper.vm.$refs.errorDialog = { open: vi.fn(), close: vi.fn() }

    await wrapper.vm.save()

    expect(wrapper.vm.errorTitle).toBe('Invalid Credentials')
    expect(wrapper.vm.errorText).toBe('BCOL API Error<br>Invalid User ID or Password')
  })

  it('sets errorText and errorTitle correctly for a 400 BCOL error with rootCause', async () => {
    const orgStore = useOrgStore()

    orgStore.updateOrg = vi.fn().mockRejectedValue({
      response: {
        status: 400,
        data: {
          errorMessage: 'API backend third party service error.',
          rootCause: {
            code: 'BCOL API Error',
            detail: null,
            message: {
              detail: 'Invalid User ID or Password',
              title: 'Invalid Credentials',
              type: 'INVALID_CREDENTIALS'
            }
          }
        }
      }
    })

    wrapper.vm.selectedPaymentMethod = PaymentTypes.CREDIT_CARD
    wrapper.vm.isBtnSaved = false
    wrapper.vm.$refs.errorDialog = { open: vi.fn(), close: vi.fn() }

    await wrapper.vm.save()

    expect(wrapper.vm.errorTitle).toBe('Invalid Credentials')
    expect(wrapper.vm.errorText).toBe('BCOL API Error<br>Invalid User ID or Password')
  })
})
