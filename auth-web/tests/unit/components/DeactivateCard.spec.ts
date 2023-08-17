import initialize from '@/plugins/i18n'
import { mount } from '@vue/test-utils'
import { Account } from '@/util/constants'
import DeactivateCard from '@/components/auth/account-deactivate/DeactivateCard.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

Vue.use(VueRouter)
Vue.use(Vuetify)
const i18n = initialize(Vue)

const vuetify = new Vuetify({})
const router = new VueRouter()

describe('Deactivated card.vue', () => {
  let wrapper: any

  afterEach(() => {
    wrapper.destroy()
  })

  it('Truthy and basic test', () => {
    wrapper = mount(DeactivateCard, {
      vuetify,
      router,
      i18n
    })

    expect(wrapper.vm).toBeTruthy()
    expect(wrapper.find("[data-test='title-deactivate']").text()).toBe('When this account is deactivated...')
    wrapper.destroy()
  })

  it('assert props.type can be set', () => {
    wrapper = mount(DeactivateCard, {
      vuetify,
      router,
      i18n,
      propsData: {
        type: Account.BASIC
      }
    })

    expect(wrapper.vm).toBeTruthy()
    expect(wrapper.props('type')).toBe(Account.BASIC)
  })

  it('assert subtitle for a default org', () => {
    wrapper = mount(DeactivateCard, {
      vuetify,
      router,
      i18n
    })

    expect(wrapper.props('type')).not.toBe(Account.PREMIUM)
    expect(wrapper.text()).not.toContain('The Pre-Authorized Debit Agreement') // this is only for premium orgs
  })
  it('assert subtitle for a premium org', async () => {
    wrapper = mount(DeactivateCard, {
      vuetify,
      router,
      i18n,
      propsData: {
        type: Account.PREMIUM
      }
    })

    expect(wrapper.props('type')).toBe(Account.PREMIUM)
    expect(wrapper.text()).toContain('The Pre-Authorized Debit Agreement') // this is only for premium orgs
  })
  it('assert subtitle for a basic org', async () => {
    wrapper = mount(DeactivateCard, {
      vuetify,
      router,
      i18n,
      propsData: {
        type: Account.BASIC
      }
    })

    expect(wrapper.props('type')).toBe(Account.BASIC)
    expect(wrapper.text()).not.toContain('The Pre-Authorized Debit Agreement') // this is only for premium orgs
  })
})
