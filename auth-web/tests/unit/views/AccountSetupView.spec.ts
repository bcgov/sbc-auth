import { createLocalVue, shallowMount } from '@vue/test-utils'
import { useOrgStore, useUserStore } from '@/stores'
import AccountSetupView from '@/views/auth/create-account/AccountSetupView.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

document.body.setAttribute('data-app', 'true')

describe('AccountSetupView.vue', () => {
  const localVue = createLocalVue()
  localVue.use(VueRouter)
  const vuetify = new Vuetify({})

  let router: VueRouter

  beforeEach(() => {
    const orgStore = useOrgStore()
    orgStore.createOrg = vi.fn().mockResolvedValue({ id: 999 })
    orgStore.syncOrganization = vi.fn().mockResolvedValue({})
    orgStore.syncMembership = vi.fn().mockResolvedValue({})

    const userStore = useUserStore()
    userStore.userContact = null
    userStore.createUserContact = vi.fn().mockResolvedValue({})
    userStore.getUserProfile = vi.fn().mockResolvedValue({})
  })

  function mountView (props) {
    router = new VueRouter({ routes: [] })
    vi.spyOn(router, 'push').mockImplementation(() => Promise.resolve() as any)
    return shallowMount(AccountSetupView, {
      localVue,
      vuetify,
      router,
      propsData: props,
      mocks: { $t: (key: string) => key }
    })
  }

  it('confirm original setup account success with no redirect url', async () => {
    const wrapper = mountView({ skipConfirmation: true, redirectToUrl: '' })

    await (wrapper.vm as any).createAccount()

    expect(router.push).toHaveBeenCalledWith('/setup-account-success')
  })

  it('carries redirectToUrl through to the success route when present', async () => {
    const confirmPath = '/vendor-linking/confirm?vendorAccountId=4082&returnUrl=' +
      encodeURIComponent('https://vendor.example.com/callback')
    const wrapper = mountView({ skipConfirmation: true, redirectToUrl: confirmPath })

    await (wrapper.vm as any).createAccount()

    expect(router.push).toHaveBeenCalledWith(
      `/setup-account-success?redirectToUrl=${encodeURIComponent(confirmPath)}`
    )
  })
})
