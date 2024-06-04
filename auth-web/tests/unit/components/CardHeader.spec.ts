import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import CardHeader from '@/components/CardHeader.vue'
import Vuetify from 'vuetify'

describe('CardHeader.vue', () => {
  let wrapper: Wrapper<any>

  beforeEach(() => {
    const localVue = createLocalVue()

    wrapper = mount(CardHeader, {
      localVue,
      vuetify: new Vuetify({}),
      propsData: {
        badgeText: 'Megatron',
        icon: 'mdi-calendar-clock',
        label: 'Optimus Prime',
        showBadge: true
      }
    })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the component properly', () => {
    expect(wrapper.findComponent(CardHeader).exists()).toBe(true)
    expect(wrapper.find('.v-card-header').exists()).toBe(true)
    expect(wrapper.find('.v-card-header').find('.v-icon').exists()).toBe(true)
    expect(wrapper.find('.v-card-header').find('.v-chip').exists()).toBe(true)
    expect(wrapper.find('.v-card-label').exists()).toBe(true)
  })

  it('shows proper components with proper content', () => {
    expect(wrapper.find('.v-card-header').find('.v-icon').attributes().class.includes('mdi-calendar-clock')).toBe(true)
    expect(wrapper.find('.v-card-label').text()).toBe('Optimus Prime')
    expect(wrapper.find('.v-card-header').find('.v-chip').text()).toBe('Megatron')
  })
})
