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
        },
        computed: {
          enableBcCccUlc () {
            return true
          }
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
    expect(wrapper.find(NumberedCompanyTooltip).exists()).toBe(false)
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
    const bulletListItems = wrapper.vm.$el.querySelectorAll('.list-item .list-item')

    expect(bulletListItems[0].textContent).toContain('Register a firm such as a sole proprietorship, a Doing Business')
    expect(bulletListItems[1].textContent).toContain('Incorporate a B.C. based company or a cooperative association.')

    // List item count will be +1 due to our fixed tooltip bullet point
    expect(bulletListItems.length).toStrictEqual(2)
  })

  it('renders the correct text and number of expansion panels', async () => {
    const expansionItems = wrapper.vm.$el.querySelectorAll('.v-expansion-panel-header')

    expect(expansionItems[0].textContent).toContain('Sole Proprietorship, DBA, and General Partnership')
    expect(expansionItems[1].textContent).toContain('B.C. Based Company')
    expect(expansionItems[2].textContent).toContain('Cooperative Association')

    // List item count will be 3
    expect(expansionItems.length).toStrictEqual(3)

    // Trigger header button clicks
    await wrapper.findAll('.v-expansion-panel-header').at(0).trigger('click')
    await wrapper.findAll('.v-expansion-panel-header').at(1).trigger('click')
    await wrapper.findAll('.v-expansion-panel-header').at(2).trigger('click')

    expect(wrapper.find('#expPnlContent1').text()).toContain('The name(s) and address(es) of the proprietor')
    expect(wrapper.find('#expPnlContent2').text()).toContain('Office addresses, director names and addresses, ' +
      'share structure')
    expect(wrapper.find('#expPnlContent3').text()).toContain('Office addresses, director names and addresses, rules of ' +
      'the association')
  })
})
