import { shallowMount } from '@vue/test-utils'
import Footer from '@/components/Footer.vue'

describe('Footer.vue', () => {
  test('set up correctly', () => {
    const wrapper = shallowMount(Footer)
    expect(wrapper.isVueInstance()).toBeTruthy()
  })
})
