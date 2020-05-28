// Libraries
import Vue from 'vue'
import Vuex from 'vuex'
import Vuetify from 'vuetify'
import { createLocalVue, mount } from '@vue/test-utils'

// Components
import BcscPanel from '@/components/auth/BcscPanel.vue'
import LearnMoreButton from '@/components/auth/common/LearnMoreButton.vue'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('MaintainBusinessView.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({})

    wrapperFactory = (propsData) => {
      return mount(BcscPanel, {
        localVue,
        store,
        vuetify,
        propsData: {
          ...propsData
        },
      })
    }

    wrapper = wrapperFactory({ userProfile: {} })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('renders the components properly', () => {
    expect(wrapper.find(BcscPanel).exists()).toBe(true)
    expect(wrapper.find(LearnMoreButton).exists()).toBe(true)
  })

  it('doesn\'t render the login or create account link when authenticated', () => {
    const authenticatedBtns = wrapper.vm.$el.querySelectorAll('.v-btn')
    const createAccountLink = wrapper.vm.$el.querySelectorAll('a')

    // Verify only the Learn More Button is rendered
    expect(authenticatedBtns.length).toStrictEqual(1)
    expect(authenticatedBtns[0]).toBeDefined()
    expect(authenticatedBtns[0].textContent).toContain('Learn More')

    // Verify the account create link is not rendered
    expect(createAccountLink.length).toStrictEqual(1)
    expect(createAccountLink[0].textContent).not.toEqual('Create a BC Registries Account')

  })

  it('renders the login button and create account link when NOT authenticated', () => {
    // Render Un-Authenticated
    const wrapper = wrapperFactory({ userProfile: null })

    const authenticatedBtns = wrapper.vm.$el.querySelectorAll('.v-btn')
    const createAccountLink = wrapper.vm.$el.querySelectorAll('a')

    expect(authenticatedBtns[0]).toBeDefined()
    expect(authenticatedBtns[0].textContent).toContain('Log in with BC Services Card')

    expect(createAccountLink[0]).toBeDefined()
    expect(createAccountLink[0].textContent).toContain('Create a BC Registries Account')

    expect(authenticatedBtns[1]).toBeDefined()
    expect(authenticatedBtns[1].textContent).toContain('Learn More')
  })

  it('renders the correct text and number of bullet points', () => {
    wrapper.vm.secureBulletPoints = [
      { text: 'Bullet 1' }, { text: 'Bullet 2' }
    ]

    wrapper.vm.easeBulletPoints = [
      { text: 'Bullet 3' }, { text: 'Bullet 4' }
    ]

    const bulletListItems = wrapper.vm.$el.querySelectorAll('.list-item')

    expect(bulletListItems[0].textContent).toContain('Bullet 1')
    expect(bulletListItems[1].textContent).toContain('Bullet 2')

    expect(bulletListItems[2].textContent).toContain('Bullet 3')
    expect(bulletListItems[3].textContent).toContain('Bullet 4')

    expect(bulletListItems.length).toStrictEqual(4)
  })
})
