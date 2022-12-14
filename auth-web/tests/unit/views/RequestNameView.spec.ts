import { createLocalVue, mount } from '@vue/test-utils'
import LearnMoreButton from '@/components/auth/common/LearnMoreButton.vue'
import NumberedCompanyTooltip from '@/components/auth/common/NumberedCompanyTooltip.vue'
import RequestNameView from '@/views/auth/home/RequestNameView.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

const mockSession = {
  'NRO_URL': 'Mock NRO URL',
  'NAME_REQUEST_URL': 'Mock Name Request URL'
}

describe('RequestNameView.vue', () => {
  let wrapper: any

  beforeEach(() => {
    sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockSession)
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({})

    wrapper = mount(RequestNameView, {
      store,
      localVue,
      vuetify,
      computed: {
        enableBcCccUlc () {
          return false
        }
      }
    })
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('renders the components properly', () => {
    expect(wrapper.find(RequestNameView).exists()).toBe(true)
    expect(wrapper.find(NumberedCompanyTooltip).exists()).toBe(true)
    expect(wrapper.find(LearnMoreButton).exists()).toBe(true)
  })

  it('renders the name request button', () => {
    const nameRequestBtn = wrapper.find('.btn-name-request')

    expect(nameRequestBtn).toBeDefined()
    expect(nameRequestBtn.text()).toContain('Request a Name')
  })

  it('renders the name request status link', () => {
    const statusLink = wrapper.find('.status-link')

    expect(statusLink).toBeDefined()
    expect(statusLink.text()).toContain('Check your Name Request Status')
  })

  it('renders the correct text and number of bullet points', () => {
    const bulletList = wrapper.vm.$el.querySelectorAll('.list-item')

    expect(bulletList[0].textContent).toContain('You can choose to have a name or use the incorporation number as ' +
      'the name of the business.')
    expect(bulletList[1].textContent).toContain('If you choose to have a name for your business, create a unique ' +
      'name that ensures the public is not confused or mislead by similar corporate names.')
    expect(bulletList[2].textContent).toContain('Submit your name choices for examination')
    expect(bulletList[3].textContent).toContain('If your name is approved')

    // List item count will be +1 due to our fixed tooltip bullet point
    expect(bulletList.length).toStrictEqual(5)
  })
})
