import UserModule from '@/store/modules/user'
import Signout from '@/components/auth/Signout.vue'
import Vuex from 'vuex'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import VuexPersistence from 'vuex-persist'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('Signout.vue', () => {
  let wrapper: Wrapper<Signout>

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const vuexPersist = new VuexPersistence({
      key: 'AUTH_WEB',
      storage: sessionStorage
    })

    const store = new Vuex.Store({
      strict: false,
      modules: {
        user: UserModule
      },
      plugins: [vuexPersist.plugin]
    })

    wrapper = mount(Signout, {
      store,
      localVue
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })
})
