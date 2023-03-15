import { createLocalVue, mount } from '@vue/test-utils'
import PaymentCard from '@/components/pay/PaymentCard.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('PaymentCard.vue', () => {
  let wrapper: any
  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    const vuetify = new Vuetify({})

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {}
    })
    const paymentCardData = {
      totalBalanceDue: 50,
      payeeName: 'BC Reg',
      cfsAccountId: 1234,
      overCredit: true,
      partialCredit: false,
      creditBalance: 6,
      credit: 10,
      paymentId: 1
    }

    const $t = () => ''
    wrapper = mount(PaymentCard, {
      propsData: {
        paymentCardData
      },
      store,
      localVue,
      vuetify,
      mocks: { $t }
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('Should Payment card div', () => {
    expect(wrapper.find('[data-test="div-bcol-payment-card"]')).toBeTruthy()
  })
})
