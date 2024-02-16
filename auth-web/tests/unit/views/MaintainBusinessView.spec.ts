import { createLocalVue, mount } from '@vue/test-utils'
import LearnMoreButton from '@/components/auth/common/LearnMoreButton.vue'
import MaintainBusinessView from '@/views/auth/home/MaintainBusinessView.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

const config = { 'REGISTRY_HOME_URL': 'hello' }

describe('MaintainBusinessView.vue', () => {
  let wrapper: any
  let wrapperFactory: any
  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    const router = new VueRouter()

    wrapperFactory = (propsData) => {
      return mount(MaintainBusinessView, {
        localVue,
        router,
        vuetify,
        propsData: {
          ...propsData
        },
        mocks: {
          $t: (mock) => mock
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
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the components properly', () => {
    expect(wrapper.findComponent(MaintainBusinessView).exists()).toBe(true)
    expect(wrapper.findComponent(LearnMoreButton).exists()).toBe(true)
  })

  it('renders the correct buttons when authenticated', () => {
    const authenticatedBtns = wrapper.vm.$el.querySelectorAll('.v-btn')
    const manageBusinessBtn = authenticatedBtns[0]
    const learnMoreBtn = authenticatedBtns[1]

    expect(manageBusinessBtn).toBeDefined()
    expect(manageBusinessBtn.textContent).toContain('Manage my Business')

    expect(learnMoreBtn).toBeDefined()
    expect(learnMoreBtn.textContent).toContain('Learn More')
  })

  it('renders the manage business button when NOT authenticated', () => {
    // Render Un-Authenticated
    const wrapper = wrapperFactory({ userProfile: null })

    const authenticatedBtns = wrapper.vm.$el.querySelectorAll('.v-btn')
    const manageBusinessBtn = authenticatedBtns[0]
    const learnMoreBtn = authenticatedBtns[1]

    expect(manageBusinessBtn).toBeDefined()
    expect(manageBusinessBtn.textContent).toContain('Manage my Business')

    expect(learnMoreBtn).toBeDefined()
    expect(learnMoreBtn.textContent).toContain('Learn More')
  })

  it('renders the correct text and number of bullet points', () => {
    const bulletListItems = wrapper.vm.$el.querySelectorAll('.list-item')
    const bulletListSubItems = wrapper.vm.$el.querySelectorAll('.list-item-sub')

    expect(bulletListItems[0].textContent).toContain('Once your business is incorporated or registered you are ' +
      'required to keep information about your business up to date with the Registry.')
    expect(bulletListItems[1].textContent).toContain('You can manage your business information using your BC ' +
      'Registries account:')

    expect(bulletListSubItems[0].textContent).toContain('See which Annual Reports are due for your corporation and ' +
      'file each year.')
    expect(bulletListSubItems[1].textContent).toContain('View and change your current directors or owners and ' +
      'addresses.')
    expect(bulletListSubItems[2].textContent).toContain('See the history of your business\' filings and download ' +
      'copies of all documents including your Statement of Registration, Certificate of Incorporation and more.')

    expect(bulletListItems.length).toStrictEqual(5)
    expect(bulletListSubItems.length).toStrictEqual(3)
  })
})
