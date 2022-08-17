import { createLocalVue, mount } from '@vue/test-utils'
import IncorpOrRegisterView from '@/views/auth/home/IncorpOrRegisterView.vue'
import LearnMoreButton from '@/components/auth/common/LearnMoreButton.vue'
import NumberedCompanyTooltip from '@/components/auth/common/NumberedCompanyTooltip.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

const config = { 'REGISTRY_HOME_URL': 'hello' }

describe('IncorpOrRegisterView.vue', () => {
  let wrapper: any
  let wrapperFactory: any
  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(VueRouter)
    const router = new VueRouter()

    const store = new Vuex.Store({})

    wrapperFactory = (propsData) => {
      return mount(IncorpOrRegisterView, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {
          ...propsData
        }
      })
    }

    wrapper = wrapperFactory({ userProfile: {} })
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('renders the components properly', () => {
    expect(wrapper.find(IncorpOrRegisterView).exists()).toBe(true)
    expect(wrapper.find(NumberedCompanyTooltip).exists()).toBe(true)
    expect(wrapper.find(LearnMoreButton).exists()).toBe(true)
  })

  it('renders the correct buttons when authenticated', () => {
    const authenticatedBtns = wrapper.vm.$el.querySelectorAll('.v-btn')
    const registryBtn = authenticatedBtns[0]
    const learnMoreBtn = authenticatedBtns[1]

    expect(registryBtn).toBeDefined()
    expect(registryBtn.textContent).toContain('Go to My Business Registry')

    expect(learnMoreBtn).toBeDefined()
    expect(learnMoreBtn.textContent).toContain('Learn More')
  })

  it('renders the registry button when NOT authenticated', () => {
    // Render Un-Authenticated
    const wrapper = wrapperFactory({ userProfile: null })

    const registryBtn = wrapper.vm.$el.querySelector('.v-btn')

    expect(registryBtn).toBeDefined()
    expect(registryBtn.textContent).toContain('Go to My Business Registry')
  })

  it('renders the registry buttn when authenticated', () => {
    // Render Un-Authenticated
    const wrapper = wrapperFactory({ userProfile: {} })

    const registryBtn = wrapper.vm.$el.querySelector('.cta-btn')

    expect(registryBtn).toBeDefined()
    expect(registryBtn.textContent).toContain('Go to My Business Registry')
  })

  it('renders the correct text and number of bullet points', () => {
    wrapper.vm.bulletPoints = [
      { text: 'Bullet 1' },
      { text: 'Bullet 2' },
      { text: 'Bullet 3' }
    ]

    const bulletListItems = wrapper.vm.$el.querySelectorAll('.list-item')

    expect(bulletListItems[0].textContent).toContain('If you have an approved Name Request')
    expect(bulletListItems[1].textContent).toContain('Bullet 1')
    expect(bulletListItems[2].textContent).toContain('Bullet 2')
    expect(bulletListItems[3].textContent).toContain('Bullet 3')

    // List item count will be +1 due to our fixed tooltip bullet point
    expect(bulletListItems.length).toStrictEqual(4)
  })
})
