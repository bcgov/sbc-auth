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
    'AUTH_API_URL': 'https://auth-api-post-dev.pathfinder.gov.bc.ca/api/v1',
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1',
    'VUE_APP_FLAVOR': 'post-mvp'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(keyCloakConfig)

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
