import LaunchTile from '@/components/LaunchTile.vue'
import { LaunchTileConfigIF } from '@/models/common'
import { mount } from '@vue/test-utils'
import { nextTick } from '@vue/composition-api'

// Mock data for the tileConfig prop
const mockTileConfig: LaunchTileConfigIF = {
  showTile: true,
  image: 'icon-drs.svg',
  title: 'Document Record Service',
  description: 'Use our document record service to create a new record or search for existing ones.',
  href: 'http://example.com/',
  actionLabel: 'Open',
  action: vi.fn(() => 'action called')
}

describe('LaunchTile.vue', () => {
  let wrapper: any

  beforeEach(() => {
    wrapper = mount(LaunchTile, {
      propsData: {
        tileConfig: mockTileConfig
      }
    })
  })

  it('renders the component when showTile is true', () => {
    expect(wrapper.find('.launch-card').exists()).toBe(true)
  })

  it('renders the image with the correct src', () => {
    const img = wrapper.find('img')
    expect(img.attributes('src')).toContain(mockTileConfig.image)
  })

  it('renders the title and description', () => {
    expect(wrapper.find('h2').text()).toBe(mockTileConfig.title)
    expect(wrapper.find('p').text()).toBe(mockTileConfig.description)
  })

  it('renders the button with the correct label and href', () => {
    const button = wrapper.find('#tile-btn')
    expect(button.text()).toContain(mockTileConfig.actionLabel)
    expect(button.attributes('href')).toBe(mockTileConfig.href)
  })

  it('calls the action method when button is clicked and href is not provided', async () => {
    // Update the props
    await wrapper.setProps({
      tileConfig: { ...mockTileConfig, href: null }
    })

    // Find the button and trigger a click event
    const button = wrapper.find('#tile-btn')
    await button.trigger('click')
    await nextTick()

    // Assert that the action method was called
    expect(mockTileConfig.action).toHaveBeenCalled()
    expect(mockTileConfig.action).toHaveReturnedWith('action called')
  })
})
