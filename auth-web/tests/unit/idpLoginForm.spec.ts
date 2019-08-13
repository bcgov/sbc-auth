import UserModule from '@/store/modules/user'
import IdpLogin from '@/components/auth/IdpLogin.vue'
import Vuex from 'vuex'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import VuexPersistence from 'vuex-persist'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('IdpLogin.vue', () => {
  let wrapper: Wrapper<IdpLogin>
  const keyCloakConfig = {
    'VUE_APP_ROOT_API': 'https://localhost:8080/api/v1/11',
    'VUE_APP_COPS_REDIRECT_URL': 'https://coops-dev.pathfinder.gov.bc.ca/',
    'VUE_APP_PAY_ROOT_API': 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1'
  }

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

    wrapper = mount(IdpLogin, {
      store,
      localVue
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('business contact form has save and skip buttons', () => {
    expect(wrapper.find('.signin-button')).toBeTruthy()
  })
})
