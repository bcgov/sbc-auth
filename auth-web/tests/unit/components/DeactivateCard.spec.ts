// TODO: Broken still
import { createLocalVue, mount } from '@vue/test-utils'
import { Account } from '@/util/constants'
import { createI18n } from 'vue-i18n-bridge'
import DeactivateCard from '@/components/auth/account-deactivate/DeactivateCard.vue'
import { config } from '@vue/test-utils'
import Vue from 'vue'
import VueCompositionAPI from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import MockI18n from '../test-utils/test-data/MockI18n'

Vue.use(VueRouter)
Vue.use(Vuetify)
const vuetify = new Vuetify({})
const router = new VueRouter()
const en = {
  businessRemovalDesc: 'i8n businessRemovalDesc',
  businessRemovalTitle: 'i8n businessRemovalTitle',
  deactivateMemberRemovalDesc: 'i8n deactivateMemberRemovalDesc',
  deactivateMemberRemovalTitle: 'i8n deactivateMemberRemovalTitle',
  padRemovalTitle: 'i8n padRemovalTitle'
}


function assertElements (wrapper: any) {
  expect(wrapper.text()).toContain(en.deactivateMemberRemovalTitle)
  expect(wrapper.text()).toContain(en.businessRemovalTitle)
  expect(wrapper.text()).toContain(en.deactivateMemberRemovalDesc)
  expect(wrapper.text()).toContain(en.businessRemovalDesc)
}

describe('Deactivated card.vue', () => {
  let wrapper: any
  const localVue = createLocalVue()
  localVue.use(Vuex)
  const i18n = MockI18n.mock(en)
  localVue.use(i18n as any, { bridge: true })
  

  beforeEach(() => {
    vi.mock('useI18n')  
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('Truthy and basic test', () => {
    wrapper = mount(DeactivateCard, {
      vuetify,
      localVue,
      router,
    })

    expect(wrapper.vm).toBeTruthy()
    expect(wrapper.find("[data-test='title-deactivate']").text()).toBe('When this account is deactivated...')
    wrapper.destroy()
  })

  it('assert props.type can be set', () => {
    wrapper = mount(DeactivateCard, {
      vuetify,
      localVue,
      router,
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
      localVue,
      router
    })

    expect(wrapper.props('type')).not.toBe(Account.PREMIUM)
    assertElements(wrapper)
    expect(wrapper.text()).not.toContain(en.padRemovalTitle) // this is only for premium orgs
  })
  it('assert subtitle for a premium org', async () => {
    wrapper = mount(DeactivateCard, {
      vuetify,
      localVue,
      router,
      propsData: {
        type: Account.PREMIUM
      }
    })

    expect(wrapper.props('type')).toBe(Account.PREMIUM)
    assertElements(wrapper)
    expect(wrapper.text()).toContain(en.padRemovalTitle) // this is only for premium orgs
  })
  it('assert subtitle for a basic org', async () => {
    wrapper = mount(DeactivateCard, {
      vuetify,
      localVue,
      router,
      propsData: {
        type: Account.BASIC
      }
    })

    expect(wrapper.props('type')).toBe(Account.BASIC)
    assertElements(wrapper)
    expect(wrapper.text()).not.toContain(en.padRemovalTitle) // this is only for premium orgs
  })
})
