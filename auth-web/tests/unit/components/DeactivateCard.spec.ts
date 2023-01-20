import { createLocalVue, mount } from '@vue/test-utils'
import { Account } from '@/util/constants'
import DeactivateCard from '@/components/auth/account-deactivate/DeactivateCard.vue'
import MockI18n from '../test-utils/test-data/MockI18n'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(VueRouter)
Vue.use(Vuetify)
const vuetify = new Vuetify({})
const router = new VueRouter()
const i18n = MockI18n.mock()

function assertElements (wrapper: any) {
  expect(wrapper.text()).toContain('i8n' + 'deactivateMemberRemovalTitle')
  expect(wrapper.text()).toContain('i8n' + 'businessRemovalTitle')
  expect(wrapper.text()).toContain('i8n' + 'deactivateMemberRemovalDesc')
  expect(wrapper.text()).toContain('i8n' + 'businessRemovalDesc')
}

describe('Deactivated card.vue', () => {
  let wrapper: any
  const localVue = createLocalVue()
  localVue.use(Vuex)
  localVue.use(i18n)

  it('Truthy and basic test', () => {
    wrapper = mount(DeactivateCard, {
      vuetify,
      localVue,
      router,
      mocks: {
        t: (mock) => mock
      }
    })

    expect(wrapper.isVueInstance()).toBeTruthy()
    expect(wrapper.find("[data-test='title-deactivate']").text()).toBe('When this account is deactivated...')
    wrapper.destroy()
  })

  it('assert props.type can be set', () => {
    wrapper = mount(DeactivateCard, {
      vuetify,
      localVue,
      router,
      mocks: {
        t: (mock) => mock
      },
      propsData: {
        type: Account.BASIC
      }
    })

    expect(wrapper.isVueInstance()).toBeTruthy()
    expect(wrapper.props('type')).toBe('BASIC')
  })

  it('assert subtitle for a default org', () => {
    const t = (params: string) => { return 'i8n' + params }

    wrapper = mount(DeactivateCard, {
      vuetify,
      localVue,
      router,
      mocks: { t }
    })

    assertElements(wrapper)
    expect(wrapper.text()).not.toContain('i8n' + 'padRemovalTitle') // this is only for premium orgs
    wrapper.destroy()
  })
  it('assert subtitle for a premium org', async () => {
    const t = (params: string) => { return 'i8n' + params }

    wrapper = mount(DeactivateCard, {
      vuetify,
      localVue,
      router,
      mocks: { t }
    })
    await wrapper.setProps({ type: 'PREMIUM' })
    assertElements(wrapper)
    expect(wrapper.text()).toContain('i8n' + 'padRemovalTitle') // this is only for premium orgs
    wrapper.destroy()
  })
  it('assert subtitle for a basic org', async () => {
    const t = (params: string) => { return 'i8n' + params }

    wrapper = mount(DeactivateCard, {
      vuetify,
      localVue,
      router,
      mocks: { t }
    })
    await wrapper.setProps({ type: 'BASIC' })
    assertElements(wrapper)
    expect(wrapper.text()).not.toContain('i8n' + 'padRemovalTitle') // this is only for premium orgs
    wrapper.destroy()
  })
})
