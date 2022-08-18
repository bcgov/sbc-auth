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
      vuetify
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
    wrapper.vm.bulletPoints = [
      { text: 'Bullet Mock 1' },
      { text: 'Bullet Mock 2' }
    ]

    const bulletList = wrapper.vm.$el.querySelectorAll('.list-item')

    expect(bulletList[0].textContent).toContain('Bullet Mock 1')
    expect(bulletList[1].textContent).toContain('Bullet Mock 2')
    expect(bulletList[2].textContent).toContain('Submit your name choices for examniation')
    expect(bulletList[3].textContent).toContain('If your name is approved')

    // List item count will be +1 due to our fixed tooltip bullet point
    expect(bulletList.length).toStrictEqual(5)
  })
})
