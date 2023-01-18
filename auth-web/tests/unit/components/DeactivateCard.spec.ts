import { createLocalVue, mount } from '@vue/test-utils'
import DeactivateCard from '@/components/auth/account-deactivate/DeactivateCard.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import i18n from '@/plugins/i18n'

Vue.use(VueRouter)
Vue.use(Vuetify)
const vuetify = new Vuetify({})
const router = new VueRouter()

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
        $t: (mock) => mock
      }
    })

    expect(wrapper.isVueInstance()).toBeTruthy()
    expect(wrapper.find("[data-test='title-deactivate']").text()).toBe('When this account is deactivated...')
    wrapper.destroy()
  })

  it('assert subtitle for a default org', () => {
    const $t = (params: string) => { return 'i8n' + params }

    wrapper = mount(DeactivateCard, {
      vuetify,
      localVue,
      router,
      mocks: { $t }
    })

    assertElements(wrapper)
    expect(wrapper.text()).not.toContain('i8n' + 'padRemovalTitle') // this is only for premium orgs
    wrapper.destroy()
  })
  it('assert subtitle for a premium org', async () => {
    const $t = (params: string) => { return 'i8n' + params }

    wrapper = mount(DeactivateCard, {
      vuetify,
      localVue,
      router,
      mocks: { $t }
    })
    await wrapper.setProps({ type: 'PREMIUM' })
    assertElements(wrapper)
    expect(wrapper.text()).toContain('i8n' + 'padRemovalTitle') // this is only for premium orgs
    wrapper.destroy()
  })
  it('assert subtitle for a basic org', async () => {
    const $t = (params: string) => { return 'i8n' + params }

    wrapper = mount(DeactivateCard, {
      vuetify,
      localVue,
      router,
      mocks: { $t }
    })
    await wrapper.setProps({ type: 'BASIC' })
    assertElements(wrapper)
    expect(wrapper.text()).not.toContain('i8n' + 'padRemovalTitle') // this is only for premium orgs
    wrapper.destroy()
  })
})
