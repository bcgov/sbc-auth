import { createLocalVue, mount } from '@vue/test-utils'
import SetupGovmAccountView from '@/views/auth/staff/SetupGovmAccountView.vue'
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

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('SetupGovmAccountView.vue', () => {
  let wrapper: any
  let store: any
  const localVue = createLocalVue()
  localVue.use(Vuex)

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
    wrapper.destroy()
  })
  beforeEach(() => {
    sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockSession)
    store = new Vuex.Store({
      state: {},
      strict: false
    })
  })

  it('Should have a h1', () => {
    wrapper = mount(SetupGovmAccountView, {
      store,
      vuetify,
      localVue,
      router,

      mocks: {
        $t: (mock) => mock
      }
    })

    expect(wrapper).toBeTruthy()
    expect(wrapper.find('h1').text()).toBe('Send Invite to Ministry Account')
  })
})
