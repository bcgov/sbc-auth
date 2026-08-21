import { createLocalVue, mount, shallowMount } from '@vue/test-utils'
import VendorLinkingAccessDeniedModal from '@/components/auth/vendor-linking/VendorLinkingAccessDeniedModal.vue'
import Vuetify from 'vuetify'
import { createI18n } from 'vue-i18n-composable'

const vuetify = new Vuetify({})

document.body.setAttribute('data-app', 'true')

const vendorLinkingMessages = {
  vendorLinkingAccessDeniedTitle: 'Access Denied: Unable to Connect',
  vendorLinkingAccessDeniedBodyIntro: 'You must have an account administrator or coordinator role to establish this connection. If you believe this is an error, please contact your account administrator at',
  vendorLinkingAccessDeniedClose: 'Close'
}

function createTestI18n () {
  return createI18n({
    locale: 'en',
    messages: {
      en: vendorLinkingMessages
    }
  })
}

describe('VendorLinkingAccessDeniedModal.vue', () => {
  it('renders access denied title and admin contact email link', async () => {
    const wrapper = mount(VendorLinkingAccessDeniedModal, {
      localVue: createLocalVue(),
      vuetify,
      i18n: createTestI18n(),
      propsData: {
        adminEmail: 'admin@example.com'
      }
    })

    wrapper.vm.open()
    await wrapper.vm.$nextTick()

    expect(wrapper.find('[data-test="dialog-header"]').text())
      .toContain('Access Denied: Unable to Connect')

    const body = wrapper.find('.vendor-linking-access-denied-dialog__text')
    expect(body.exists()).toBe(true)
    expect(body.text()).toContain('account administrator or coordinator role')

    const emailLink = wrapper.find('a[href="mailto:admin@example.com"]')
    expect(emailLink.exists()).toBe(true)
    expect(emailLink.text()).toBe('admin@example.com')

    wrapper.destroy()
  })

  it('exposes open and close methods for parent flow', () => {
    const wrapper = shallowMount(VendorLinkingAccessDeniedModal, {
      localVue: createLocalVue(),
      vuetify,
      i18n: createTestI18n()
    })

    expect(typeof wrapper.vm.open).toBe('function')
    expect(typeof wrapper.vm.close).toBe('function')

    wrapper.destroy()
  })
})
