import { createLocalVue, mount } from '@vue/test-utils'

import DocumentService from '@/services/document.services'
import TermsOfUseDocumentView from '@/views/auth/TermsOfUseDocumentView.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import { createI18n } from 'vue-i18n-composable'
import flushPromises from 'flush-promises'
import { useOrgStore } from '@/stores/org'

Vue.use(Vuetify)
Vue.use(VueRouter)
const router = new VueRouter()
const vuetify = new Vuetify({})

document.body.setAttribute('data-app', 'true')

describe('TermsOfUseDocumentView.vue', () => {
  describe('account terms type', () => {
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

      wrapper = mount(TermsOfUseDocumentView, {
        localVue,
        router,
        vuetify,
        i18n,
        propsData: { termsType: 'account' },
        stubs: {
          TermsOfUse: true
        }
      })
    })

    afterEach(() => {
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

    it('renders the account TermsOfUse component without loading a document by default', () => {
      expect(wrapper.vm.termsType).toBe('account')
      expect(wrapper.find('[data-test="terms-content"]').exists()).toBe(false)
    })
  })

  describe('api terms type', () => {
    const TERMS_LOAD_FAILED_MESSAGE = 'We were not able to load the terms of use. Please refresh the page or try again later.'
    let apiWrapper: any
    let getTermsOfService: any

    const mountApi = (termsType = 'api') => mount(TermsOfUseDocumentView, {
      localVue: createLocalVue(),
      router,
      vuetify,
      i18n: createI18n({ locale: 'en', messages: { en: { tos_title: 'BC Registry Terms and Conditions' } } }),
      propsData: { termsType },
      stubs: { TermsOfUse: true }
    })

    beforeEach(() => {
      getTermsOfService = vi.spyOn(DocumentService, 'getTermsOfService')
        .mockResolvedValue({ data: { content: '<p>The API terms</p>' } } as any)
      vi.spyOn(console, 'error').mockImplementation(() => {})
    })

    afterEach(() => {
      vi.restoreAllMocks()
      apiWrapper.destroy()
    })

    it('shows a spinner while the terms are loading', () => {
      getTermsOfService.mockReturnValue(new Promise(() => {}))
      apiWrapper = mountApi()

      expect(apiWrapper.find('[data-test="terms-loading"]').exists()).toBe(true)
      expect(apiWrapper.find('[data-test="terms-content"]').exists()).toBe(false)
    })

    it('loads and renders the API terms with the API title', async () => {
      apiWrapper = mountApi()
      await flushPromises()

      expect(getTermsOfService).toHaveBeenCalledWith('termsofuse_api')
      expect(apiWrapper.find('h1').text()).toBe('API Terms of Use for all products')
      expect(apiWrapper.find('[data-test="terms-content"]').html()).toContain('<p>The API terms</p>')
      expect(apiWrapper.find('[data-test="terms-loading"]').exists()).toBe(false)
      expect(apiWrapper.findComponent({ name: 'TermsOfUse' }).exists()).toBe(false)
    })

    it('shows an error when the terms request fails', async () => {
      getTermsOfService.mockRejectedValue(new Error('boom'))
      apiWrapper = mountApi()
      await flushPromises()

      expect(apiWrapper.find('[data-test="terms-load-error"]').text()).toContain(TERMS_LOAD_FAILED_MESSAGE)
      expect(apiWrapper.find('[data-test="terms-content"]').exists()).toBe(false)
    })

    it('shows an error when the terms response has no content', async () => {
      getTermsOfService.mockResolvedValue({ data: {} } as any)
      apiWrapper = mountApi()
      await flushPromises()

      expect(apiWrapper.find('[data-test="terms-load-error"]').text()).toContain(TERMS_LOAD_FAILED_MESSAGE)
    })

    it('loads the API terms when the terms type changes on a reused view', async () => {
      apiWrapper = mountApi('account')
      await flushPromises()
      expect(getTermsOfService).not.toHaveBeenCalled()

      await apiWrapper.setProps({ termsType: 'api' })
      await flushPromises()

      expect(getTermsOfService).toHaveBeenCalledWith('termsofuse_api')
      expect(apiWrapper.find('[data-test="terms-loading"]').exists()).toBe(false)
      expect(apiWrapper.find('[data-test="terms-content"]').html()).toContain('<p>The API terms</p>')
    })

    it('clears a load error when switching back to the account terms', async () => {
      getTermsOfService.mockRejectedValue(new Error('boom'))
      apiWrapper = mountApi()
      await flushPromises()
      expect(apiWrapper.find('[data-test="terms-load-error"]').exists()).toBe(true)

      await apiWrapper.setProps({ termsType: 'account' })
      await flushPromises()

      expect(apiWrapper.find('[data-test="terms-load-error"]').exists()).toBe(false)
      expect(apiWrapper.findComponent({ name: 'TermsOfUse' }).exists()).toBe(true)
    })

    it('ignores a failed API terms response after switching to the account terms', async () => {
      let rejectRequest: (e: Error) => void
      getTermsOfService.mockReturnValue(new Promise((resolve, reject) => { rejectRequest = reject }))
      apiWrapper = mountApi()

      await apiWrapper.setProps({ termsType: 'account' })
      rejectRequest(new Error('boom'))
      await flushPromises()

      expect(apiWrapper.find('[data-test="terms-load-error"]').exists()).toBe(false)
      expect(apiWrapper.findComponent({ name: 'TermsOfUse' }).exists()).toBe(true)
    })

    it('falls back to the account terms for an unknown terms type', async () => {
      apiWrapper = mountApi('unknown')
      await flushPromises()

      expect(getTermsOfService).not.toHaveBeenCalled()
      expect(apiWrapper.findComponent({ name: 'TermsOfUse' }).exists()).toBe(true)
    })
  })
})
