import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import SignoutView from '@/views/auth/SignoutView.vue'
import UserModule from '@/store/modules/user'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('SignoutView.vue', () => {
  let wrapper: Wrapper<SignoutView>
  const config = {
    'REGISTRY_HOME_URL': 'https://localhost:8080/'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({
      strict: false,
      modules: {
        user: UserModule
      }
    })

    wrapper = mount(SignoutView, {
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
