import { createLocalVue, mount } from '@vue/test-utils'
import SetupGovmAccountForm from '@/components/auth/staff/SetupGovmAccountForm.vue'
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

describe('SetupGovmAccountForm.vue', () => {
  let wrapper: any
  let store: any
  const localVue = createLocalVue()
  localVue.use(Vuex)

  const orgModule = {
    namespaced: true,
    state: {},
    actions: {
      createOrgByStaff: jest.fn(),
      createInvitation: jest.fn()
    }
  }

  beforeEach(() => {
    sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockSession)
    store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        org: orgModule

      }
    })
  })

  it('Should have h4 title', () => {
    wrapper = mount(SetupGovmAccountForm, {
      store,
      vuetify,
      localVue,
      router,
      mocks: {
        $t: (mock) => mock
      }
    })

    expect(wrapper.isVueInstance()).toBeTruthy()
    expect(wrapper.find('h4').text()).toBe('Enter Ministry Information for this account')
    wrapper.destroy()
  })
})
