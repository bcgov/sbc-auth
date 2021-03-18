import { createLocalVue, mount } from '@vue/test-utils'

import GovmAccountSetupView from '@/views/auth/create-account/GovmAccountSetupView.vue'
// import { AccountStatus } from '@/util/constants'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'

import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)
const router = new VueRouter()
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

const mockSession = {
  'NRO_URL': 'Mock NRO URL',
  'NAME_REQUEST_URL': 'Mock Name Request URL'
}

describe('GovmAccountSetupView.vue', () => {
  let wrapper: any
  let userModule: any

  beforeEach(() => {
    sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockSession)
    const localVue = createLocalVue()
    localVue.use(Vuex)

    userModule = {
      namespaced: true,
      state: {
        userProfile: {}
      },
      actions: {
        getUserProfile: jest.fn()
      }
    }

    const orgModule = {
      namespaced: true,
      state: {
        // currentOrganization: {
        //   statusCode: AccountStatus.NSF_SUSPENDED
        // }
      }
    }

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        user: userModule,
        org: orgModule
      }
    })

    wrapper = mount(GovmAccountSetupView, {
      store,
      localVue,
      router,
      vuetify,
      mocks: {
        $t: (mock) => mock
      },
      computed: {
        isAccountStatusNsfSuspended: Boolean
      }
    })
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('should render page title', () => {
    expect(wrapper.find('h1').text()).toBe('Create a Ministry Account')
  })

  it('should render page title icon color correctly', () => {
    expect(wrapper.find(ModalDialog).exists()).toBe(true)
  })

  it('should call createAccount on emit', async () => {
    wrapper.vm.$emit('createAccount')

    await wrapper.vm.$nextTick() // Wait until $emits have been handled

    // assert event has been emitted
    expect(wrapper.emitted().createAccount).toBeTruthy()
  })
})
