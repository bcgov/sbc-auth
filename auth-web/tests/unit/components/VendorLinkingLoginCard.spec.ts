import { createLocalVue, mount } from '@vue/test-utils'
import ConfigHelper from '@/util/config-helper'
import VendorLinkingLoginCard from '@/components/auth/vendor-linking/VendorLinkingLoginCard.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

document.body.setAttribute('data-app', 'true')

// The confirm URL pushed to /signin/:idpHint/:redirectUrl(.*) goes through two decode
// passes before use in production: once by vue-router's own param matching, then again by
// SigninView.vue's explicit decodeURIComponent. Mirroring both here is what actually proves
// the component's double-encoding survives the real pipeline, not just a single decode.
function decodeAsProductionDoes (encoded: string): string {
  return decodeURIComponent(decodeURIComponent(encoded))
}

describe('VendorLinkingLoginCard.vue', () => {
  const localVue = createLocalVue()
  localVue.use(VueRouter)
  const vuetify = new Vuetify({})
  const VENDOR_ACCOUNT_ID = '123'

  let router: VueRouter

  function mountCard (returnUrl: string) {
    router = new VueRouter({ routes: [] })
    vi.spyOn(router, 'push').mockImplementation(() => Promise.resolve() as any)
    return mount(VendorLinkingLoginCard, {
      localVue,
      vuetify,
      router,
      propsData: { vendorAccountId: VENDOR_ACCOUNT_ID, returnUrl },
      mocks: { $t: (key: string) => key }
    })
  }

  function expectedConfirmUrl (returnUrl: string): string {
    return `${ConfigHelper.getSelfURL()}/vendor-linking/confirm` +
      `?vendorAccountId=${VENDOR_ACCOUNT_ID}&returnUrl=${encodeURIComponent(returnUrl)}`
  }

  it('pushes to /signin/bcsc/... with the confirm URL intact after decoding it as production does', async () => {
    const returnUrl = 'https://vendor.example.com/callback'
    const wrapper = mountCard(returnUrl)

    await wrapper.find("[data-test='vendor-linking-continue-bcsc']").trigger('click')

    const pushedPath = (router.push as any).mock.calls[0][0] as string
    const match = pushedPath.match(/^\/signin\/bcsc\/(.+)$/)
    expect(match).not.toBeNull()
    expect(decodeAsProductionDoes(match[1])).toBe(expectedConfirmUrl(returnUrl))
  })

  it('pushes to /signin/bceid/... on the BCeID button', async () => {
    const returnUrl = 'https://vendor.example.com/callback'
    const wrapper = mountCard(returnUrl)

    await wrapper.find("[data-test='vendor-linking-continue-bceid']").trigger('click')

    const pushedPath = (router.push as any).mock.calls[0][0] as string
    expect(pushedPath.startsWith('/signin/bceid/')).toBe(true)
  })

  it('survives a returnUrl that carries its own & -joined query params without truncation', async () => {
    const returnUrl = 'https://vendor.example.com/callback?ref=abc&x=1'
    const wrapper = mountCard(returnUrl)

    await wrapper.find("[data-test='vendor-linking-continue-bcsc']").trigger('click')

    const pushedPath = (router.push as any).mock.calls[0][0] as string
    const match = pushedPath.match(/^\/signin\/bcsc\/(.+)$/)
    const decodedConfirmUrl = decodeAsProductionDoes(match[1])

    expect(decodedConfirmUrl).toBe(expectedConfirmUrl(returnUrl))
    const decodedReturnUrl = new URL(decodedConfirmUrl).searchParams.get('returnUrl')
    expect(decodedReturnUrl).toBe(returnUrl)
  })
})
