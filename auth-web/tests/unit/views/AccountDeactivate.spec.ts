import { createLocalVue, mount } from '@vue/test-utils'
import AccountDeactivate from '@/views/auth/AccountDeactivate.vue'
import DeactivateCard from '@/components/auth/account-deactivate/DeactivateCard.vue'
import MockI18n from '../test-utils/test-data/MockI18n'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)
const router = new VueRouter()
const vuetify = new Vuetify({})

const en = {
  test: 'Test'
}

const i18n = MockI18n.mock(en)

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('AccountDeactivate.vue', () => {
  let wrapper: any
  let userModule: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(i18n)

    const orgModule = {
      namespaced: true,
      state: {
      }
    }

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        org: orgModule
      }
    })

    wrapper = mount(AccountDeactivate, {
      store,
      localVue,
      router,
      vuetify
    })
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
    wrapper.destroy()
  })

  it('AccountDeactivate is a Vue instance', () => {
    expect(wrapper).toBeTruthy()
  })
  it('AccountDeactivate contains the card', () => {
    expect(wrapper.find(DeactivateCard).exists()).toBe(true)
  })
})
