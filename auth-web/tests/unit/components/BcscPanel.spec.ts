import { createLocalVue, mount } from '@vue/test-utils'
import BcscPanel from '@/components/auth/home/BcscPanel.vue'
import LearnMoreButton from '@/components/auth/common/LearnMoreButton.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import flushPromises from 'flush-promises'

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

    wrapper = wrapperFactory({ userProfile: {} })
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the components properly', () => {
    expect(wrapper.findComponent(BcscPanel).exists()).toBe(true)
    expect(wrapper.findComponent(LearnMoreButton).exists()).toBe(true)
  })

  it('doesn\'t render the login or create account link when authenticated', () => {
    const authenticatedBtns = wrapper.vm.$el.querySelectorAll('.v-btn')
    const createAccountLink = wrapper.vm.$el.querySelector('.cta-btn')

    // Verify only the Learn More Button is rendered
    expect(authenticatedBtns.length).toStrictEqual(1)
    expect(authenticatedBtns[0]).toBeDefined()
    expect(authenticatedBtns[0].textContent).toContain('Learn More')

    // Verify the account create link is not rendered
    expect(createAccountLink).toBeNull()
  })

  it('renders the login button and create account link when NOT authenticated', () => {
    // Render Un-Authenticated
    const wrapper = wrapperFactory({ userProfile: null })

    const authenticatedBtns = wrapper.vm.$el.querySelectorAll('.v-btn')
    const mobileCardLink = wrapper.vm.$el.querySelectorAll('a')
    const createAccountLink = wrapper.vm.$el.querySelector('.cta-btn')

    expect(authenticatedBtns[0]).toBeDefined()
    expect(authenticatedBtns[0].textContent).toContain('Create a BC Registries Account')

    expect(mobileCardLink[0]).toBeDefined()
    expect(mobileCardLink[0].textContent).toContain('set up a mobile card')

    expect(createAccountLink).toBeDefined()
    expect(createAccountLink.textContent).toContain('Create a BC Registries Account')

    expect(authenticatedBtns[1]).toBeDefined()
    expect(authenticatedBtns[1].textContent).toContain('Learn More')
  })

  it('renders the correct text and number of bullet points', async () => {
    wrapper.vm.secureBulletPoints = [
      { text: 'Bullet 1' }, { text: 'Bullet 2' }
    ]

    wrapper.vm.easeBulletPoints = [
      { text: 'Bullet 3' }, { text: 'Bullet 4' }
    ]
    await flushPromises()

    const bulletListItems = wrapper.vm.$el.querySelectorAll('.list-item')

    expect(bulletListItems[0].textContent).toContain('Bullet 1')
    expect(bulletListItems[1].textContent).toContain('Bullet 2')

    expect(bulletListItems[3].textContent).toContain('Bullet 3')
    expect(bulletListItems[4].textContent).toContain('Bullet 4')

    expect(bulletListItems.length).toStrictEqual(5)
  })
})
