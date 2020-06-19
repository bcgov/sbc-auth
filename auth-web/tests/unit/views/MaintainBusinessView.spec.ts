import { createLocalVue, mount } from '@vue/test-utils'
import LearnMoreButton from '@/components/auth/common/LearnMoreButton.vue'
import MaintainBusinessView from '@/views/auth/MaintainBusinessView.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

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
      return mount(MaintainBusinessView, {
        localVue,
        store,
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
    expect(wrapper.find(MaintainBusinessView).exists()).toBe(true)
    expect(wrapper.find(LearnMoreButton).exists()).toBe(true)
  })

  it('renders the correct buttons when authenticated', () => {
    const authenticatedBtns = wrapper.vm.$el.querySelectorAll('.v-btn')
    const manageBusinessBtn = authenticatedBtns[0]
    const learnMoreBtn = authenticatedBtns[1]

    expect(manageBusinessBtn).toBeDefined()
    expect(manageBusinessBtn.textContent).toContain('Manage an Existing Business')

    expect(learnMoreBtn).toBeDefined()
    expect(learnMoreBtn.textContent).toContain('Learn More')
  })

  it('renders the login button when NOT authenticated', () => {
    // Render Un-Authenticated
    const wrapper = wrapperFactory({ userProfile: null })

    const authenticatedBtns = wrapper.vm.$el.querySelectorAll('.v-btn')
    const loginBtn = authenticatedBtns[0]
    const learnMoreBtn = authenticatedBtns[1]

    expect(loginBtn).toBeDefined()
    expect(loginBtn.textContent).toContain('Create a BC Registries Account')

    expect(learnMoreBtn).toBeDefined()
    expect(learnMoreBtn.textContent).toContain('Learn More')
  })

  it('renders the correct text and number of bullet points', () => {
    wrapper.vm.bulletPoints = [
      { text: 'Bullet 1' },
      { text: 'Bullet 2',
        subText: [
          { text: 'Sub Bullet 3' },
          { text: 'Sub Bullet 4' }
        ]
      }
    ]

    const bulletListItems = wrapper.vm.$el.querySelectorAll('.list-item')
    const bulletListSubItems = wrapper.vm.$el.querySelectorAll('.list-item-sub')

    expect(bulletListItems[0].textContent).toContain('Bullet 1')
    expect(bulletListItems[1].textContent).toContain('Bullet 2')

    expect(bulletListSubItems[0].textContent).toContain('Sub Bullet 3')
    expect(bulletListSubItems[1].textContent).toContain('Sub Bullet 4')

    expect(bulletListItems.length).toStrictEqual(4)
    expect(bulletListSubItems.length).toStrictEqual(2)
  })
})
