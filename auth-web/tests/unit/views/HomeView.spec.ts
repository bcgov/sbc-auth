import { createLocalVue, mount } from '@vue/test-utils'
import BcscPanel from '@/components/auth/home/BcscPanel.vue'
import HomeView from '@/views/auth/home/HomeView.vue'
import InfoStepper from '@/components/auth/home/InfoStepper.vue'
import TestimonialQuotes from '@/components/auth/home/TestimonialQuotes.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)
Vue.use(VueRouter)

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

const mockSession = {
  'NRO_URL': 'Mock NRO URL',
  'NAME_REQUEST_URL': 'Mock Name Request URL'
}

describe('HomeView.vue', () => {
  let wrapper: any
  let userModule: any

  beforeEach(() => {
    sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(mockSession)
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(VueRouter)

    const router = new VueRouter()
    const vuetify = new Vuetify({})

    userModule = {
      namespaced: true,
      state: {
        userProfile: {
        }
      },
      actions: {
        getUserProfile: vi.fn()
      }
    }

    const orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {
        }
      },
      actions: {
        syncOrganizations: vi.fn(),
        syncCurrentOrganization: vi.fn()
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

    wrapper = mount(HomeView, {
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
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the sub-components properly', () => {
    expect(wrapper.findComponent(InfoStepper).exists()).toBe(true)
    expect(wrapper.findComponent(TestimonialQuotes).exists()).toBe(true)
    expect(wrapper.findComponent(BcscPanel).exists()).toBe(true)
  })

  it('renders the correct buttons when authenticated', () => {
    const nameRequestBtn = wrapper.find('.btn-name-request')
    const manageBusinessBtn = wrapper.findAll('.cta-btn-auth').at(0)

    expect(nameRequestBtn.exists()).toBe(true)
    expect(nameRequestBtn.text()).toContain('Request a Name')

    expect(manageBusinessBtn.exists()).toBe(true)
    expect(manageBusinessBtn.text()).toContain('Manage my Business')
  })

  it('renders the correct buttons when not authenticated', async () => {
    // Render Un-authenticated
    userModule.state.userProfile = null
    await flushPromises()
    const loginBtn = wrapper.findAll('.cta-btn').at(0)
    const nameRequestBtn = wrapper.find('.btn-name-request')

    const createAccountLink = wrapper.find('.cta-btn')

    expect(loginBtn.exists()).toBe(true)
    expect(loginBtn.text()).toContain('Create a BC Registries Account')

    expect(nameRequestBtn.exists()).toBe(true)
    expect(nameRequestBtn.text()).toContain('Request a Name')

    expect(createAccountLink.exists()).toBe(true)
    expect(createAccountLink.text()).toContain('Create a BC Registries Account')
  })
})
