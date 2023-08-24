import { createLocalVue, shallowMount } from '@vue/test-utils'
import { GLInfo } from '@/models/Organization'
import PaymentInformation from '@/components/auth/staff/review-task/PaymentInformation.vue'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('PaymentInformation.vue', () => {
  let wrapper: any
  let wrapperFactory: any
  const revenueAccount: GLInfo =
    {
      client: '112',
      projectCode: '3200000',
      responsibilityCentre: '32041',
      serviceLine: '35301',
      stob: '1278'
    }
  const props = {
    tabNumber: 3,
    title: 'Payment Information',
    currentOrganizationGLInfo: revenueAccount,
    canSelect: true
  }

  beforeEach(() => {
    const localVue = createLocalVue()

    wrapperFactory = (propsData) => {
      return shallowMount(PaymentInformation, {
        localVue,
        vuetify,
        propsData: {
          ...propsData
        }
      })
    }

    wrapper = wrapperFactory(props)
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the AgreementInformation components properly ', () => {
    expect(wrapper.findComponent(PaymentInformation).exists()).toBe(true)
  })

  it('renders proper GLInfo content', () => {
    expect(wrapper.find('[data-test="payment-info-client"]').text()).toBe('112')
    expect(wrapper.find('[data-test="payment-info-responsibilityCentre"]').text()).toBe('32041')
    expect(wrapper.find('[data-test="payment-info-serviceLine"]').text()).toBe('35301')
    expect(wrapper.find('[data-test="payment-info-stob"]').text()).toBe('1278')
    expect(wrapper.find('[data-test="payment-info-projectCode"]').text()).toBe('3200000')
  })
})
