import { createLocalVue, shallowMount } from '@vue/test-utils'
import { useOrgStore, useUserStore } from '@/stores'
import AccountSelectList from '@/components/auth/common/AccountSelectList.vue'
import LinkingKeysService from '@/services/linkingKeys.services'
import UserService from '@/services/user.services'
import VendorLinkingView from '@/views/auth/VendorLinkingView.vue'
import Vuetify from 'vuetify'
import can from '@/directives/can'
import flushPromises from 'flush-promises'

document.body.setAttribute('data-app', 'true')

describe('VendorLinkingView.vue', () => {
  let wrapper: any
  const localVue = createLocalVue()
  localVue.directive('can', can)
  const vuetify = new Vuetify({})
  const $t = (key: string) => key

  const VENDOR_ACCOUNT_ID = '55'
  const RETURN_URL = 'https://vendor.example.com/callback?ref=abc'

  beforeEach(() => {
    const userStore = useUserStore()
    userStore.currentUserAccountSettings = [
      { id: 10, label: 'DEV SK OB1', type: 'ACCOUNT' }
    ] as any

    const orgStore = useOrgStore()
    orgStore.getOrgAdminContact = vi.fn().mockResolvedValue({
      street: '111-5657 Spring Garden Rd', city: 'Halifax', region: 'NS', postalCode: 'B3J 3R4', country: 'CA'
    })

    vi.spyOn(UserService, 'getMembership').mockResolvedValue({ data: { membershipTypeCode: 'ADMIN' } } as any)

    // jsdom's window.location.replace is non-configurable, so it can't be spied on directly.
    delete (window as any).location
    window.location = { replace: vi.fn() } as any
  })

  afterEach(() => {
    wrapper?.destroy()
    vi.restoreAllMocks()
  })

  async function selectTheOnlyAccount () {
    wrapper = shallowMount(VendorLinkingView, {
      localVue,
      vuetify,
      propsData: { vendorAccountId: VENDOR_ACCOUNT_ID, returnUrl: RETURN_URL },
      mocks: { $t }
    })
    await flushPromises()
    wrapper.findComponent(AccountSelectList).vm.$emit('select', 10)
    await flushPromises()
  }

  it('redirects to the callback URL with the key and account id on success, preserving existing query params', async () => {
    vi.spyOn(LinkingKeysService, 'createOrgLinkingKey').mockResolvedValue({
      data: { id: 1, accountId: 10, vendorAccountId: 55, linkingKey: 'the-key-value', status: 'ACTIVE' }
    } as any)

    await selectTheOnlyAccount()

    expect(wrapper.vm.resultSuccess).toBe(true)
    wrapper.vm.redirectNow()

    expect(window.location.replace).toHaveBeenCalledWith(
      'https://vendor.example.com/callback?ref=abc&linkingKey=the-key-value&accountId=10'
    )
  })

  it('shows the redirect-URL-specific failure copy and callback params when the API rejects the URL', async () => {
    vi.spyOn(LinkingKeysService, 'createOrgLinkingKey').mockRejectedValue({
      response: { status: 400, data: { code: 'REDIRECT_URL_INVALID', message: 'not registered for this vendor' } }
    })

    await selectTheOnlyAccount()

    expect(wrapper.vm.resultSuccess).toBe(false)
    expect(wrapper.vm.failureTitle).toBe('vendorLinkingResultFailureRedirectTitle')
    expect(wrapper.vm.failureBody).toBe('vendorLinkingResultFailureRedirectBody')

    // The rejected returnUrl is untrusted (unregistered for this vendor) so we don't provide the return button
    expect(wrapper.find("[data-test='vendor-linking-result-return']").exists()).toBe(false)
    expect(window.location.replace).not.toHaveBeenCalled()
  })

  it('shows the generic failure copy and a working return button for a non-redirect-URL error', async () => {
    vi.spyOn(LinkingKeysService, 'createOrgLinkingKey').mockRejectedValue({
      response: { status: 500, data: { message: 'server exploded' } }
    })

    await selectTheOnlyAccount()

    expect(wrapper.vm.failureTitle).toBe('vendorLinkingResultFailureGenericTitle')
    expect(wrapper.vm.failureBody).toBe('vendorLinkingResultFailureGenericBody')
    expect(wrapper.find("[data-test='vendor-linking-result-return']").exists()).toBe(true)
  })

  it('shows the inline no-eligible-accounts message with no auto-redirect when the user has no accounts at all', async () => {
    const userStore = useUserStore()
    userStore.currentUserAccountSettings = []
    userStore.getUserAccountSettings = vi.fn().mockResolvedValue([])

    wrapper = shallowMount(VendorLinkingView, {
      localVue,
      vuetify,
      propsData: { vendorAccountId: VENDOR_ACCOUNT_ID, returnUrl: RETURN_URL },
      mocks: { $t }
    })
    await flushPromises()

    expect(wrapper.vm.step).toBe('SELECT_ACCOUNT')
    expect(wrapper.vm.eligibleAccounts).toHaveLength(0)
    expect(wrapper.findComponent(AccountSelectList).exists()).toBe(false)
    expect(wrapper.find("[data-test='vendor-linking-no-eligible-accounts-alert']").exists()).toBe(true)
  })

  it('shows the inline no-eligible-accounts message when the user has accounts but none as admin/coordinator', async () => {
    vi.spyOn(UserService, 'getMembership').mockResolvedValue({ data: { membershipTypeCode: 'USER' } } as any)

    wrapper = shallowMount(VendorLinkingView, {
      localVue,
      vuetify,
      propsData: { vendorAccountId: VENDOR_ACCOUNT_ID, returnUrl: RETURN_URL },
      mocks: { $t }
    })
    await flushPromises()

    expect(wrapper.vm.step).toBe('SELECT_ACCOUNT')
    expect(wrapper.vm.eligibleAccounts).toHaveLength(0)
    expect(wrapper.find("[data-test='vendor-linking-no-eligible-accounts-alert']").exists()).toBe(true)
  })
})
