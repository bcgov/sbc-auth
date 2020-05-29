import { createLocalVue, mount } from '@vue/test-utils'
import LearnMoreButton from '@/components/auth/common/LearnMoreButton.vue'
import NumberedCompanyTooltip from '@/components/auth/common/NumberedCompanyTooltip.vue'
import RequestNameView from '@/views/auth/RequestNameView.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('RequestNameView.vue', () => {
  let wrapper: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({})

    wrapper = mount(RequestNameView, {
      store,
      localVue,
      vuetify
    })

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
    const nameRequestBtn = wrapper.vm.$el.querySelector('.v-btn')

    expect(nameRequestBtn).toBeDefined()
    expect(nameRequestBtn.textContent).toContain('Request a Name')
  })

  it('renders the name request link', () => {
    const nameRequestLink = wrapper.vm.$el.querySelectorAll('a')

    expect(nameRequestLink[1]).toBeDefined()
    expect(nameRequestLink[1].textContent).toContain('Check your Name Request Status')
  })

  it('renders the correct text and number of bullet points', () => {
    wrapper.vm.bulletPoints = [
      { text: 'Bullet 1' }, { text: 'Bullet 2' }, { text: 'Bullet 3' }
    ]

    const bulletListItems = wrapper.vm.$el.querySelectorAll('.list-item')

    expect(bulletListItems[0].textContent).toContain('Bullet 1')
    expect(bulletListItems[1].textContent).toContain('Bullet 2')
    expect(bulletListItems[2].textContent).toContain('Bullet 3')
    expect(bulletListItems[3].textContent).toContain('You can choose to incorporate')

    // List item count will be +1 due to our fixed tooltip bullet point
    expect(bulletListItems.length).toStrictEqual(4)
  })
})
