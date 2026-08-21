import { createLocalVue, shallowMount } from '@vue/test-utils'
import VendorLinkingWarningAlert from '@/components/auth/vendor-linking/VendorLinkingWarningAlert.vue'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})

document.body.setAttribute('data-app', 'true')

describe('VendorLinkingWarningAlert.vue', () => {
  it('renders title, body, and note when all are provided', () => {
    const wrapper = shallowMount(VendorLinkingWarningAlert, {
      localVue: createLocalVue(),
      vuetify,
      propsData: {
        title: 'Some Title',
        body: 'Some body text.',
        note: 'Some note text.'
      }
    })

    expect(wrapper.text()).toContain('Some Title')
    expect(wrapper.text()).toContain('Some body text.')
    expect(wrapper.text()).toContain('Note:')
    expect(wrapper.text()).toContain('Some note text.')
  })

  it('renders only body when title and note are omitted', () => {
    const wrapper = shallowMount(VendorLinkingWarningAlert, {
      localVue: createLocalVue(),
      vuetify,
      propsData: {
        body: 'Just the body.'
      }
    })

    expect(wrapper.text()).toBe('Just the body.')
  })
})
