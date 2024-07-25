import { createLocalVue, mount } from '@vue/test-utils'
import ShortNameRefundView from '@/views/pay/eft/ShortNameRefundView.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import sinon from 'sinon'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('ShortNameRefundView.vue', () => {
  let wrapper
  const localVue = createLocalVue()
  const vuetify = new Vuetify({})
  let sandbox

  beforeEach(() => {
    sandbox = sinon.createSandbox()
    wrapper = mount(ShortNameRefundView, {
      propsData: {
        shortNameDetails: { shortName: 'TEST', creditsRemaining: '500.0' },
        unsettledAmount: '100.0'
      },
      localVue,
      vuetify
    })
  })

  afterEach(() => {
    wrapper.destroy()
    sandbox.restore()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the component correctly', () => {
    expect(wrapper.find('.view-header__title').text()).toBe('Refund Information')
    expect(wrapper.find('[data-test="refundAmount"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="casSupplierNumber"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="email"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="staffComment"]').exists()).toBe(true)
  })

  it('return to previous page when cancel button is clicked', async () => {
    const router = new VueRouter()
    wrapper = mount(ShortNameRefundView, {
      propsData: {
        shortNameDetails: { shortName: 'TEST', creditsRemaining: '500.0' },
        unsettledAmount: '100.0'
      },
      localVue,
      vuetify,
      router
    })
    const push = sinon.stub(wrapper.vm.$router, 'push')

    await wrapper.find('[data-test="btn-edit-cancel"]').trigger('click')

    expect(push.calledWith({ name: 'shortnamedetails' })).toBe(true)
    push.restore()
  })
})
