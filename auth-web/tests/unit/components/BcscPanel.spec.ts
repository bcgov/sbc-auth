import { createLocalVue, mount } from '@vue/test-utils'
import BcscPanel from '@/components/auth/home/BcscPanel.vue'
import LearnMoreButton from '@/components/auth/common/LearnMoreButton.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('BcscPanel.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(VueRouter)
    const router = new VueRouter()
    const store = new Vuex.Store({})

    wrapperFactory = (propsData) => {
      return mount(BcscPanel, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {
          ...propsData
        }
      })
    }

    wrapper = wrapperFactory({ user: { firstname: 'test', lastname: 'test' } })
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the components properly', () => {
    expect(wrapper.findComponent(BcscPanel).exists()).toBe(true)
    expect(wrapper.findComponent(LearnMoreButton).exists()).toBe(true)
  })

  it('renders the correct text and number of bullet points', async () => {
    expect(wrapper.findAll('.list-item').length).toStrictEqual(4)
    expect(wrapper.findAll('.list-item').at(0).text())
      .toContain(`A mobile card is a representation of your BC Services Card on your mobile device. It's used to ` +
    `prove who you are when you log in to access government services online.`)
    expect(wrapper.findAll('.list-item').at(1).text())
      .toContain('Only your name and a unique identifier is stored on the mobile device.')
    expect(wrapper.findAll('.list-item').at(2).text())
      .toContain('It normally takes about 5 minutes to')
    expect(wrapper.findAll('.list-item').at(3).text())
      .toContain(`You can verify your identity by video right from your mobile device. You don't need to go in person` +
      ` unless you can't verify by video.`)
  })

  it('doesn\'t render the login or create account link when authenticated', () => {
    // Verify only the Learn More Button is rendered
    expect(wrapper.find('.cta-btn').exists()).toBe(false)
    expect(wrapper.findAll('.v-btn').length).toBe(1)
    expect(wrapper.find('.learn-more-btn')).toBeDefined()
    expect(wrapper.find('.learn-more-btn').text()).toContain('Learn More')
  })

  it('renders the login button and create account link when NOT authenticated', () => {
    // Render Un-Authenticated
    const wrapper = wrapperFactory({ userProfile: null })

    const authenticatedBtns = wrapper.vm.$el.querySelectorAll('.v-btn')
    const mobileCardLink = wrapper.findAll('a').at(0)
    const createAccountLink = wrapper.find('.cta-btn')

    expect(authenticatedBtns[0]).toBeDefined()
    expect(authenticatedBtns[0].textContent).toContain('Create a BC Registries Account')

    expect(mobileCardLink.exists()).toBe(true)
    expect(mobileCardLink.text()).toContain('set up a mobile card')

    expect(createAccountLink.exists()).toBe(true)
    expect(createAccountLink.text()).toContain('Create a BC Registries Account')

    expect(authenticatedBtns[1]).toBeDefined()
    expect(authenticatedBtns[1].textContent).toContain('Learn More')
  })
})
