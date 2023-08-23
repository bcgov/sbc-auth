import { createLocalVue, mount } from '@vue/test-utils'
import TestimonialQuotes from '@/components/auth/home/TestimonialQuotes.vue'
import Vuetify from 'vuetify'

document.body.setAttribute('data-app', 'true')

describe('TestimonialQuotes.vue', () => {
  let wrapper: any

  beforeEach(() => {
    const localVue = createLocalVue()

    const vuetify = new Vuetify({})

    wrapper = mount(TestimonialQuotes, {
      localVue,
      vuetify
    })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('it renders quotes correctly', () => {
    expect(wrapper.find('.quote-container').exists()).toBe(true)
    expect(wrapper.find('.quote-text').text()).toBe('We are really excited by the idea of incorporating as a Benefit' +
    ' Company, it really makes sense for us and the way we want to run our business.')
    expect(wrapper.find('.quote-author').text()).toBe('– Business Founder')
  })
})
