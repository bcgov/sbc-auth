import '@/composition-api-setup'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import AccountDeactivate from '@/views/auth/AccountDeactivate.vue'
import DeactivateCard from '@/components/auth/account-deactivate/DeactivateCard.vue'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import i18n from '@/plugins/i18n'

Vue.use(Vuetify)
Vue.use(VueI18n)
Vue.use(VueRouter)
const router = new VueRouter()
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('AccountDeactivate.vue', () => {
  let wrapper: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

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

    wrapper = shallowMount(AccountDeactivate, {
      store,
      localVue,
      i18n,
      router,
      vuetify
    })
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('AccountDeactivate is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })
  it('AccountDeactivate contains the card', () => {
    expect(wrapper.findComponent(DeactivateCard).exists()).toBe(true)
  })
})
