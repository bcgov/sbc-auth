import { createLocalVue, mount, shallowMount } from '@vue/test-utils'
import VendorLinkingAccessDeniedModal from '@/components/auth/vendor-linking/VendorLinkingAccessDeniedModal.vue'
import VendorLinkingAccountSelectAlert from '@/components/auth/vendor-linking/VendorLinkingAccountSelectAlert.vue'
import VendorLinkingLoginAlert from '@/components/auth/vendor-linking/VendorLinkingLoginAlert.vue'
import Vuetify from 'vuetify'
import { createI18n } from 'vue-i18n-composable'

const vuetify = new Vuetify({})

document.body.setAttribute('data-app', 'true')

const vendorLinkingMessages = {
  vendorLinkingLoginAlertTitle: 'Connecting to a Third-Party Service Account',
  vendorLinkingLoginAlertBody: 'Logging in will link your account to the service provider account.',
  vendorLinkingLoginAlertNote: 'Note: You must have an account administrator or coordinator role to establish this connection.',
  vendorLinkingAccountSelectAlert: 'You have multiple accounts associated with your profile. Only accounts where you are an administrator or coordinator are shown below.',
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

describe('VendorLinkingLoginAlert.vue', () => {
  it('renders login redirect alert copy from Figma', () => {
    const wrapper = shallowMount(VendorLinkingLoginAlert, {
      localVue: createLocalVue(),
      vuetify,
      i18n: createTestI18n()
    })

    const alert = wrapper.find('[data-test="vendor-linking-login-alert"]')
    expect(alert.exists()).toBe(true)
    expect(alert.text()).toContain('Connecting to a Third-Party Service Account')
    expect(alert.text()).toContain('Logging in will link your account to the service provider account.')
    expect(alert.text()).toContain('account administrator or coordinator role')

    wrapper.destroy()
  })
})

describe('VendorLinkingAccountSelectAlert.vue', () => {
  it('renders account selection alert copy from Figma', () => {
    const wrapper = shallowMount(VendorLinkingAccountSelectAlert, {
      localVue: createLocalVue(),
      vuetify,
      i18n: createTestI18n()
    })

    const alert = wrapper.find('[data-test="vendor-linking-account-select-alert"]')
    expect(alert.exists()).toBe(true)
    expect(alert.text()).toContain('Only accounts where you are an administrator or coordinator are shown below.')

    wrapper.destroy()
  })
})

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
