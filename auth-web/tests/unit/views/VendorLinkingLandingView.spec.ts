import { createLocalVue, shallowMount } from '@vue/test-utils'
import { SessionStorageKeys } from '@/util/constants'
import VendorLinkingLandingView from '@/views/auth/VendorLinkingLandingView.vue'
import VendorLinkingLoginCard from '@/components/auth/vendor-linking/VendorLinkingLoginCard.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

document.body.setAttribute('data-app', 'true')

describe('VendorLinkingLandingView.vue', () => {
  const localVue = createLocalVue()
  localVue.use(VueRouter)
  const vuetify = new Vuetify({})
  const VALID_VENDOR_ACCOUNT_ID = '123'
  const VALID_RETURN_URL = 'https://vendor.example.com/callback'

  let router: VueRouter

  afterEach(() => {
    sessionStorage.removeItem(SessionStorageKeys.KeyCloakToken)
  })

  function mountView (props) {
    router = new VueRouter({ routes: [] })
    vi.spyOn(router, 'push').mockImplementation(() => Promise.resolve() as any)
    return shallowMount(VendorLinkingLandingView, {
      localVue,
      vuetify,
      router,
      propsData: props,
      mocks: { $t: (key: string) => key }
    })
  }

  it('shows the error state when vendorAccountId is missing', () => {
    const wrapper = mountView({ vendorAccountId: '', returnUrl: VALID_RETURN_URL })
    expect(wrapper.text()).toContain('Unable to Connect')
    expect(wrapper.findComponent(VendorLinkingLoginCard).exists()).toBe(false)
  })

  it('shows the error state when vendorAccountId is non-numeric', () => {
    const wrapper = mountView({ vendorAccountId: 'abc', returnUrl: VALID_RETURN_URL })
    expect(wrapper.text()).toContain('Unable to Connect')
  })

  it('shows the error state when returnUrl is not a valid http(s) URL', () => {
    const wrapper = mountView({ vendorAccountId: VALID_VENDOR_ACCOUNT_ID, returnUrl: 'not-a-url' })
    expect(wrapper.text()).toContain('Unable to Connect')
  })

  it('renders the login card for valid params when signed out, without redirecting', () => {
    const wrapper = mountView({ vendorAccountId: VALID_VENDOR_ACCOUNT_ID, returnUrl: VALID_RETURN_URL })
    expect(wrapper.findComponent(VendorLinkingLoginCard).exists()).toBe(true)
    expect(router.push).not.toHaveBeenCalled()
  })

  it('forwards straight to the confirm route when already signed in', () => {
    sessionStorage.setItem(SessionStorageKeys.KeyCloakToken, 'a-token')
    mountView({ vendorAccountId: VALID_VENDOR_ACCOUNT_ID, returnUrl: VALID_RETURN_URL })
    expect(router.push).toHaveBeenCalledWith({
      path: '/vendor-linking/confirm',
      query: { vendorAccountId: VALID_VENDOR_ACCOUNT_ID, returnUrl: VALID_RETURN_URL }
    })
  })

  it('does not auto-forward when already signed in but params are invalid', () => {
    sessionStorage.setItem(SessionStorageKeys.KeyCloakToken, 'a-token')
    mountView({ vendorAccountId: '', returnUrl: VALID_RETURN_URL })
    expect(router.push).not.toHaveBeenCalled()
  })
})
