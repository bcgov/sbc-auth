import { createLocalVue, shallowMount } from '@vue/test-utils'
import AccountCreationSuccessView from '@/views/auth/create-account/AccountCreationSuccessView.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import { useOrgStore } from '@/stores/org'

document.body.setAttribute('data-app', 'true')

describe('AccountCreationSuccessView.vue', () => {
  const localVue = createLocalVue()
  localVue.use(VueRouter)
  const vuetify = new Vuetify({})

  let router: VueRouter

  function mountView (props = {}) {
    router = new VueRouter({ routes: [] })
    vi.spyOn(router, 'push').mockImplementation(() => Promise.resolve() as any)
    return shallowMount(AccountCreationSuccessView, {
      localVue,
      vuetify,
      router,
      propsData: props,
      mocks: { $t: (key: string) => key }
    })
  }

  it('shows the existing completion screen and does not navigate when redirectToUrl is absent', () => {
    const orgStore = useOrgStore()
    orgStore.currentOrganization = { id: 1, accessType: 'REGULAR' } as any
    const wrapper = mountView()

    expect(wrapper.find('h1').exists()).toBe(true)
    expect(wrapper.find("[data-test='btn-goto-home']").exists()).toBe(true)
    expect(router.push).not.toHaveBeenCalled()
  })

  it('navigates straight to redirectToUrl without rendering the button screen when present', () => {
    const confirmPath = '/vendor-linking/confirm?vendorAccountId=4082&returnUrl=' +
      encodeURIComponent('https://vendor.example.com/callback')
    mountView({ redirectToUrl: confirmPath })

    expect(router.push).toHaveBeenCalledWith(confirmPath)
  })
})
