import { createLocalVue, mount } from '@vue/test-utils'
import DeactivateCard from '@/components/auth/account-deactivate/DeactivateCard.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(VueRouter)
Vue.use(Vuetify)
const vuetify = new Vuetify({})
const router = new VueRouter()

const mockSession = {
  'NRO_URL': 'Mock NRO URL',
  'NAME_REQUEST_URL': 'Mock Name Request URL'
}

describe('SetupGovmAccountForm.vue', () => {
  let wrapper: any
  let store: any
  const localVue = createLocalVue()
  localVue.use(Vuex)

  it('Truthy', () => {
    wrapper = mount(DeactivateCard, {
      store,
      vuetify,
      localVue,
      router,
      mocks: {
        $t: (mock) => mock
      }
    })

    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('assert title', () => {
    wrapper = mount(DeactivateCard, {
      store,
      vuetify,
      localVue,
      router,
      mocks: {
        $t: (mock) => mock
      }
    })

    expect(wrapper.isVueInstance()).toBeTruthy()
    expect(wrapper.find("[data-test='title-deactivate']").text()).toBe('When this account is deactivated...')
  })
  it('assert subtitle', () => {
    const $t = (params: string) => 'team member message'

    wrapper = mount(DeactivateCard, {
      store,
      vuetify,
      localVue,
      router,
      mocks: { $t }
    })

    expect(wrapper.isVueInstance()).toBeTruthy()
    expect(wrapper.text()).toContain('team member message')
  })
})
