import { shallowMount } from '@vue/test-utils'
import Header from '@/components/Header.vue'

describe('Footer.vue', () => {
  test('set up correctly', () => {
    const wrapper = shallowMount(Header)
    expect(wrapper.isVueInstance()).toBeTruthy()
  })
})
