import { createLocalVue, mount } from '@vue/test-utils'
import PayWithCreditCard from '@/components/pay/PayWithCreditCard.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('PayWithCreditCard.vue', () => {
  let wrapper: any
  beforeEach(() => {
    const $t = () => ''
    const localVue = createLocalVue()
    localVue.use(Vuex)
    const vuetify = new Vuetify({})
    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {}
    })

    wrapper = mount(PayWithCreditCard, {
      store,
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
