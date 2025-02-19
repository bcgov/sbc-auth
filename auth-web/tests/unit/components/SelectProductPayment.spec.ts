import { Account, PaymentTypes } from '@/util/constants'
import { createLocalVue, mount } from '@vue/test-utils'
import SelectProductPayment from '@/components/auth/create-account/SelectProductPayment.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import can from '@/directives/can'
import { useOrgStore } from '@/stores'

describe('SelectProductPayment.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  const config = {
    'AUTH_API_URL': 'https://localhost:8080/api/v1/11',
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()

    const vuetify = new Vuetify({})
    localVue.directive('can', can)
    const orgStore = useOrgStore()
    orgStore.setCurrentOrganization({
      id: 1,
      name: 'Test Org'
    })

    const router = new VueRouter()

    wrapperFactory = (propsData) => {
      return mount(SelectProductPayment, {
        localVue,
        router,
        vuetify,
        propsData: {
          ...propsData
        }
      })
    }

    wrapper = wrapperFactory({ currentOrgType: Account.PREMIUM })

    vi.resetModules()
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('initial selection should be empty', () => {
    expect(wrapper.vm.$data.selectedPaymentMethod).toBeFalsy()
  })

  it('currentOrganization should be on state, used for BCOL and PAD', async () => {
    console.log(wrapper.vm.currentOrganization)
    expect(wrapper.vm.currentOrganization).toBeTruthy()
  })

  it('correct isPaymentValid', async () => {
    wrapper.setData({ selectedPaymentMethod: PaymentTypes.PAD })
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.isPaymentValid).toBe(wrapper.vm.isPADValid)
    wrapper.setData({ selectedPaymentMethod: PaymentTypes.BCOL })
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.isPaymentValid).toBe(wrapper.vm.currentOrganization.bcolProfile?.password)
    wrapper.setData({ selectedPaymentMethod: PaymentTypes.EJV })
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.isPaymentValid).toBe(wrapper.vm.isEJVValid)
    wrapper.setData({ selectedPaymentMethod: PaymentTypes.CREDIT_CARD })
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.isPaymentValid).toBe(!!wrapper.vm.selectedPaymentMethod)
  })

  it('correct finish button text', async () => {
    wrapper = wrapperFactory({ govmAccount: true })
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.finishButtonText).toBe('Next')
    wrapper = wrapperFactory({ govmAccount: false, readOnly: false })
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.finishButtonText).toBe('Create Account')
    wrapper = wrapperFactory({ govmAccount: false, readOnly: true })
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.finishButtonText).toBe('Submit')
  })
})
