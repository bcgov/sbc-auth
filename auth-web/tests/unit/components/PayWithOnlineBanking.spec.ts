import { createLocalVue, mount } from '@vue/test-utils'
import PayWithOnlineBanking from '@/components/pay/PayWithOnlineBanking.vue'
import Vuetify from 'vuetify'

describe('PayWithOnlineBanking.vue', () => {
  let wrapper: any
  beforeEach(() => {
    const localVue = createLocalVue()
    const vuetify = new Vuetify({})

    const onlineBankingData = {
      totalBalanceDue: 10,
      payeeName: 'BC Reg',
      cfsAccountId: 1234,
      overCredit: true,
      partialCredit: false,
      creditBalance: 6,
      credit: 0
    }

    const $t = () => ''
    wrapper = mount(PayWithOnlineBanking, {
      propsData: {
        onlineBankingData
      },
      localVue,
      vuetify,
      mocks: { $t }
    })

    vi.resetModules()
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('Should have Title section', () => {
    expect(wrapper.find('.heading-info')).toBeTruthy()
  })
})
