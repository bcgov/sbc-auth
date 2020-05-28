// Libraries
import Vue from 'vue'
import Vuex from 'vuex'
import Vuetify from 'vuetify'
import { createLocalVue, mount } from '@vue/test-utils'

// Components
import IncorpOrRegisterView from '@/views/auth/IncorpOrRegisterView.vue'
import LearnMoreButton from '@/components/auth/common/LearnMoreButton.vue'
import NumberedCompanyTooltip from '@/components/auth/common/NumberedCompanyTooltip.vue'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('IncorpOrRegisterView.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({})

    wrapperFactory = (propsData) => {
      return mount(IncorpOrRegisterView, {
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
    expect(wrapper.find(IncorpOrRegisterView).exists()).toBe(true)
    expect(wrapper.find(NumberedCompanyTooltip).exists()).toBe(true)
    expect(wrapper.find(LearnMoreButton).exists()).toBe(true)
  })

  it('renders the correct buttons when authenticated', () => {
    const authenticatedBtns = wrapper.vm.$el.querySelectorAll('.v-btn')
    const namedCompBtn = authenticatedBtns[0]
    const numberedCompBtn = authenticatedBtns[1]

    expect(namedCompBtn).toBeDefined()
    expect(namedCompBtn.textContent).toContain('Incorporate a Named Company')

    expect(numberedCompBtn).toBeDefined()
    expect(numberedCompBtn.textContent).toContain('Incorporate a Numbered Company')
  })

  it('renders the login button when NOT authenticated', () => {
    // Render Un-Authenticated
    const wrapper = wrapperFactory({ userProfile: null })

    const loginBtn = wrapper.vm.$el.querySelector('.v-btn')

    expect(loginBtn).toBeDefined()
    expect(loginBtn.textContent).toContain('Log in with BC Services Card')
  })

  it('renders the create account link when NOT authenticated', () => {
    // Render Un-Authenticated
    const wrapper = wrapperFactory({ userProfile: null })

    const createAccountLink = wrapper.vm.$el.querySelector('a')

    expect(createAccountLink).toBeDefined()
    expect(createAccountLink.textContent).toContain('Create a BC Registries Account')
  })

  it('renders the correct text and number of bullet points', () => {
    wrapper.vm.bulletPoints = [
      { text: 'Bullet 1' }, { text: 'Bullet 2' }, { text: 'Bullet 3' }
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
