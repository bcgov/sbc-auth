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

  it('clears the form when the cancel button is clicked', async () => {
    await wrapper.setData({
      refundAmount: 100.00,
      casSupplierNum: 'CAS-123',
      email: 'test@example.com',
      staffComment: 'Test comment'
    })

    const cancelButton = wrapper.find('[data-test="btn-edit-routing-cancel"]')
    await cancelButton.trigger('click')

    expect(wrapper.vm.$data.refundAmount).toBe(undefined)
    expect(wrapper.vm.$data.casSupplierNum).toBe('')
    expect(wrapper.vm.$data.email).toBe('')
    expect(wrapper.vm.$data.staffComment).toBe('')
  })
})
