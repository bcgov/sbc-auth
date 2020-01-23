import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import Signin from '@/views/auth/SigninView.vue'
import UserModule from '@/store/modules/user'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('Signin.vue', () => {
  let wrapper: Wrapper<Signin>
  const keyCloakConfig = {
    'VUE_APP_ROOT_API': 'https://localhost:8080/api/v1/11',
    'VUE_APP_COPS_REDIRECT_URL': 'https://coops-dev.pathfinder.gov.bc.ca/',
    'VUE_APP_AUTH_ROOT_API': 'https://auth-api-post-dev.pathfinder.gov.bc.ca/api/v1',
    'VUE_APP_PAY_ROOT_API': 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1',
    'VUE_APP_FLAVOR': 'post-mvp'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(keyCloakConfig)

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({
      strict: false,
      modules: {
        user: UserModule
      }
    })

    let vuetify = new Vuetify({})

    wrapper = mount(Signin, {
      store,
      vuetify,
      localVue
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })
})
