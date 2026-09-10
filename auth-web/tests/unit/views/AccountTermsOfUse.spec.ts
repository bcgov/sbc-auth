import { createLocalVue, mount } from '@vue/test-utils'

import AccountTermsOfUse from '@/views/auth/AccountTermsOfUse.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import { createI18n } from 'vue-i18n-composable'
import { useOrgStore } from '@/stores/org'

Vue.use(Vuetify)
Vue.use(VueRouter)
const router = new VueRouter()
const vuetify = new Vuetify({})

document.body.setAttribute('data-app', 'true')

describe('AccountTermsOfUse.vue', () => {
  let wrapper: any

  beforeEach(() => {
    const localVue = createLocalVue()
    const orgStore = useOrgStore()
    orgStore.currentOrganization = {
      id: 1234,
      name: 'testOrg'
    } as any

    const i18n = createI18n({
      locale: 'en',
      messages: {
        en: {
          tos_title: 'BC Registry Terms and Conditions',
          govm_tos_title: 'Ministry Use Memorandum of Understanding (MOU)'
        }
      }
    })

    wrapper = mount(AccountTermsOfUse, {
      localVue,
      router,
      vuetify,
      i18n,
      stubs: {
        TermsOfUse: true
      }
    })
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the page title', () => {
    expect(wrapper.find('h1').text()).toBe('BC Registry Terms and Conditions')
  })

  it('renders the TermsOfUse component', () => {
    expect(wrapper.findComponent({ name: 'TermsOfUse' }).exists()).toBe(true)
  })

  it('builds the back to account link from the current organization id', () => {
    expect(wrapper.vm.accountInfoUrl).toBe('/account/1234/settings')
    expect(wrapper.find('.crumbs a').attributes('href')).toBe('#/account/1234/settings')
  })

  it('updates the back to account link when the current organization changes', async () => {
    const orgStore = useOrgStore()
    orgStore.currentOrganization = {
      id: 5678,
      name: 'anotherOrg'
    } as any
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.accountInfoUrl).toBe('/account/5678/settings')
  })
})
