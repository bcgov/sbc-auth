import { createLocalVue, mount } from '@vue/test-utils'
import BcscPanel from '@/components/auth/BcscPanel.vue'
import HomeViewDev from '@/views/auth/HomeViewDev.vue'
import InfoStepper from '@/components/auth/stepper/InfoStepper.vue'
import LoginBCSC from '@/components/auth/LoginBCSC.vue'
import TestimonialQuotes from '@/components/auth/TestimonialQuotes.vue'
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
  'NRO_URL': 'Mock Url'
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

    wrapper = mount(HomeViewDev, {
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
  })

  it('is a Vue instance', async () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('renders the sub-components properly', () => {
    expect(wrapper.find(InfoStepper).exists()).toBe(true)
    expect(wrapper.find(TestimonialQuotes).exists()).toBe(true)
    expect(wrapper.find(BcscPanel).exists()).toBe(true)
  })

  it('renders the correct buttons when authenticated', () => {
    const bannerBtns = wrapper.vm.$el.querySelectorAll('.cta-btn')
    const nameRequestBtn = bannerBtns[0]
    const namedCompBtn = bannerBtns[1]
    const numberedCompBtn = bannerBtns[2]
    const manageBusinessBtn = bannerBtns[3]
    const loginBtn = bannerBtns[4]

    expect(nameRequestBtn).toBeDefined()
    expect(nameRequestBtn.textContent).toContain('Request a Name')

    expect(namedCompBtn).toBeDefined()
    expect(namedCompBtn.textContent).toContain('Incorporate a Named Benefit Company')

    expect(numberedCompBtn).toBeDefined()
    expect(numberedCompBtn.textContent).toContain('Incorporate a Numbered Benefit Company')

    expect(manageBusinessBtn).toBeDefined()
    expect(manageBusinessBtn.textContent).toContain('Manage an Existing Business')

    // Verify the the login btn is undefined
    expect(loginBtn).toBeUndefined()
  })

  it('renders the correct buttons when not authenticated', async () => {
    // Render Un-authenticated
    userModule.state.userProfile = null

    const bannerBtns = wrapper.vm.$el.querySelectorAll('.cta-btn')
    const loginBtn = bannerBtns[0]
    const nameRequestBtn = bannerBtns[1]

    const createAccountLink = wrapper.vm.$el.querySelector('.create-account-link')

    expect(loginBtn).toBeDefined()
    expect(loginBtn.textContent).toContain('Log in with BC Services Card')

    expect(nameRequestBtn).toBeDefined()
    expect(nameRequestBtn.textContent).toContain('Request a Name')

    expect(createAccountLink).toBeDefined()
    expect(createAccountLink.textContent).toContain('Create a BC Registries Account')
  })

  it('renders the LoginBCSC when the create account dialog is called', async () => {
    userModule.state.userProfile = null

    const createAccountLink = wrapper.vm.$el.querySelector('.create-account-link')

    expect(createAccountLink).toBeDefined()
    expect(createAccountLink.textContent).toContain('Create a BC Registries Account')

    // Verify Dialog and LoginBCSC are not rendered until called
    expect(wrapper.find(LoginBCSC).exists()).toBe(false)

    await createAccountLink.click()

    expect(wrapper.find(LoginBCSC).exists()).toBe(true)
  })
})
