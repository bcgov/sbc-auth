import { createLocalVue, mount } from '@vue/test-utils'
import ShortNameAccountLink from '@/components/pay/eft/ShortNameAccountLink.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import can from '@/directives/can'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('ShortNameAccountLink.vue', () => {
  let wrapper: any
  const localVue = createLocalVue()
  localVue.directive('can', can)
  const vuetify = new Vuetify({})

  beforeEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    const $t = () => ''
    wrapper = mount(ShortNameAccountLink, {
      localVue,
      vuetify,
      propsData: {
        shortNameDetails: { shortName: 'SHORTNAME' }
      },
      mocks: { $t
      }
    })
    expect(wrapper.vm).toBeTruthy()
  })

  it('validate shortname is unlinked', () => {
    const $t = () => ''
    wrapper = mount(ShortNameAccountLink, {
      localVue,
      vuetify,
      propsData: {
        shortNameDetails: { shortName: 'SHORTNAME' }
      },
      mocks: { $t
      }
    })
    expect(wrapper.find('.unlinked-text').text())
      .toContain('Payment from this short name is not linked with an account yet.')
    expect(wrapper.find('#link-shortname-btn').exists()).toBe(true)
  })

  it('validate shortname is linked', () => {
    const shortNameDetails = {
      shortName: 'SHORTNAME',
      accountId: 1234,
      accountName: 'TEST ACCOUNT'
    }
    const $t = () => ''
    wrapper = mount(ShortNameAccountLink, {
      localVue,
      vuetify,
      propsData: {
        shortNameDetails: shortNameDetails
      },
      mocks: { $t
      }
    })

    expect(wrapper.find('.linked-text').text())
      .toContain(`All payments from ${shortNameDetails.shortName} will be applied to:`)
    expect(wrapper.find('.linked-text').text())
      .toContain(`${shortNameDetails.accountId} ${shortNameDetails.accountName}`)
    expect(wrapper.find('#link-shortname-btn').exists()).toBe(false)
  })
})
