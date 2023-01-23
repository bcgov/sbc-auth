import { createLocalVue, mount } from '@vue/test-utils'
import AccountDeactivate from '@/views/auth/AccountDeactivate.vue'
import DeactivateCard from '@/components/auth/account-deactivate/DeactivateCard.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import i18n from '@/plugins/i18n'

Vue.use(Vuetify)
Vue.use(VueRouter)
const router = new VueRouter()
const vuetify = new Vuetify({})

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
      vuetify,
      mocks: {
        $t: (mock) => mock
      }
    })
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
  })

  it('AccountDeactivate is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })
  it('AccountDeactivate contains the card', () => {
    expect(wrapper.find(DeactivateCard).exists()).toBe(true)
  })
})
