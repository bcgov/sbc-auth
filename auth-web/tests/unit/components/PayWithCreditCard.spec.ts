import { createLocalVue, mount } from '@vue/test-utils'
import PayWithCreditCard from '@/components/pay/PayWithCreditCard.vue'
import Vuetify from 'vuetify'

describe('PayWithCreditCard.vue', () => {
  let wrapper: any
  beforeEach(() => {
    const $t = () => ''
    const localVue = createLocalVue()
    const vuetify = new Vuetify({})

    wrapper = mount(PayWithCreditCard, {
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
})
