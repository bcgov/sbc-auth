import { createLocalVue, mount } from '@vue/test-utils'
import PaymentErrorMessage from '@/components/pay/common/PaymentErrorMessage.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('PaymentErrorMessage.vue', () => {
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
    const PaymentErrorMessageData = {
      errorType: 'PAYMENT_GENERIC_ERROR',
      backUrl: '',
      tryAgainURL: ''
    }

    const $t = () => ''
    wrapper = mount(PaymentErrorMessage, {
      propsData: {
        PaymentErrorMessageData
      },
      store,
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

  it('Should Payment card div', () => {
    expect(wrapper.find('[data-test="pay-error"]')).toBeTruthy()
  })
})
