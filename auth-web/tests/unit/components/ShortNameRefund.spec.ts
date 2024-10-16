import { createLocalVue, mount } from '@vue/test-utils'
import { Role } from '@/util/constants'
import ShortNameRefund from '@/components/pay/eft/ShortNameRefund.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import sinon from 'sinon'
import { useUserStore } from '@/stores'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('ShortNameRefund.vue', () => {
  let wrapper
  const localVue = createLocalVue()
  const vuetify = new Vuetify({})
  let sandbox

  beforeEach(() => {
    sandbox = sinon.createSandbox()

    const userStore = useUserStore()
    userStore.currentUser = {
      roles: [Role.EftRefundApprover]
    } as any

    wrapper = mount(ShortNameRefund, {
      propsData: {
        shortNameDetails: { shortName: 'SHORTNAME', id: 1 },
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
    expect(wrapper.find('.card-title').text()).toContain('Short Name Refund')
    expect(wrapper.find('.card-content span').text())
      .toContain('No refund initiated. SBC Finance can initiate refund if a CAS supplier number is created for the short name.')
  })
})
