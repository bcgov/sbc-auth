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
const router = new VueRouter()
const vuetify = new Vuetify({})

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
    sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockSession)
    const localVue = createLocalVue()
    localVue.use(Vuex)

    userModule = {
      namespaced: true,
      state: {
        userProfile: {
        }
      },
      actions: {
        getUserProfile: jest.fn()
      }
    }

    const orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {
        }
      },
      actions: {
        syncOrganizations: jest.fn(),
        syncCurrentOrganization: jest.fn()
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
    jest.resetModules()
    jest.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper).toBeTruthy()
  })

  it('renders the sub-components properly', () => {
    expect(wrapper.find(InfoStepper).exists()).toBe(true)
    expect(wrapper.find(TestimonialQuotes).exists()).toBe(true)
    expect(wrapper.find(BcscPanel).exists()).toBe(true)
  })

  it('renders the correct buttons when authenticated', () => {
    const bannerBtns = wrapper.vm.$el.querySelectorAll('.cta-btn-auth')
    const nameRequestBtn = wrapper.vm.$el.querySelector('.btn-name-request')
    const manageBusinessBtn = bannerBtns[0]

    expect(nameRequestBtn).toBeDefined()
    expect(nameRequestBtn.textContent).toContain('Request a Name')

    expect(manageBusinessBtn).toBeDefined()
    expect(manageBusinessBtn.textContent).toContain('Manage my Business')
  })

  it('renders the correct buttons when not authenticated', async () => {
    // Render Un-authenticated
    userModule.state.userProfile = null
    await flushPromises()
    const bannerBtns = wrapper.vm.$el.querySelectorAll('.cta-btn')
    const loginBtn = bannerBtns[0]
    const nameRequestBtn = wrapper.vm.$el.querySelector('.btn-name-request')

    const createAccountLink = wrapper.vm.$el.querySelector('.cta-btn')

    expect(loginBtn).toBeDefined()
    expect(loginBtn.textContent).toContain('Create a BC Registries Account')

    expect(nameRequestBtn).toBeDefined()
    expect(nameRequestBtn.textContent).toContain('Request a Name')

    expect(createAccountLink).toBeDefined()
    expect(createAccountLink.textContent).toContain('Create a BC Registries Account')
  })
})
