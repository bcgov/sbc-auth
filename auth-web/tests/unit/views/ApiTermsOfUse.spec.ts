import { createLocalVue, mount } from '@vue/test-utils'
import ApiTermsOfUse from '@/views/auth/ApiTermsOfUse.vue'
import DocumentService from '@/services/document.services'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'
import { useOrgStore } from '@/stores/org'

document.body.setAttribute('data-app', 'true')

const TERMS_MISSING_MESSAGE = 'API Terms of Use are missing. API keys cannot be created until they are available.'
const TERMS_LOAD_FAILED_MESSAGE = 'The API Terms of Use could not be loaded. Please refresh the page to try again.'

const httpError = (response: any) => Object.assign(new Error('request failed'), { response })

describe('ApiTermsOfUse.vue', () => {
  const localVue = createLocalVue()
  localVue.use(VueRouter)
  const vuetify = new Vuetify({})

  let router: VueRouter
  let wrapper: any
  let getTermsOfService: any
  let acceptApiTerms: any

  function mountView () {
    router = new VueRouter({ routes: [] })
    vi.spyOn(router, 'push').mockImplementation(() => Promise.resolve() as any)
    return mount(ApiTermsOfUse, {
      localVue,
      vuetify,
      router,
      propsData: { orgId: '123' }
    })
  }

  async function mountAndLoad () {
    wrapper = mountView()
    await flushPromises()
  }

  const agreeButton = () => wrapper.find('[data-test="accept-api-terms-button"]')

  async function clickAgree () {
    agreeButton().trigger('click')
    await flushPromises()
  }

  beforeEach(() => {
    getTermsOfService = vi.spyOn(DocumentService, 'getTermsOfService')
      .mockResolvedValue({ data: { versionId: 'k01', content: '<p>The API terms</p>' } } as any)
    acceptApiTerms = vi.fn(() => Promise.resolve({ isAccepted: true }))
    useOrgStore().acceptApiTerms = acceptApiTerms as any
  })

  afterEach(() => {
    vi.restoreAllMocks()
    wrapper.destroy()
  })

  it('shows a spinner while the terms are loading', () => {
    getTermsOfService.mockReturnValue(new Promise(() => {}))
    wrapper = mountView()

    expect(wrapper.find('[data-test="api-terms-loading"]').exists()).toBe(true)
    expect(agreeButton().attributes('disabled')).toBeDefined()
  })

  it('renders the latest terms and their version', async () => {
    await mountAndLoad()

    expect(getTermsOfService).toHaveBeenCalledWith('termsofuse_api')
    expect(wrapper.find('[data-test="api-terms-content"]').html()).toContain('<p>The API terms</p>')
    expect(wrapper.find('[data-test="api-terms-version"]').text()).toBe('Version k01')
    expect(wrapper.find('[data-test="api-terms-load-error"]').exists()).toBe(false)
    expect(agreeButton().attributes('disabled')).toBeUndefined()
  })

  it('links back to developer access from the breadcrumb and the Decline button', async () => {
    await mountAndLoad()

    expect(wrapper.find('.crumbs a').attributes('href')).toBe('#/account/123/settings/developer-access')
    expect(wrapper.find('[data-test="decline-api-terms-button"]').attributes('href'))
      .toBe('#/account/123/settings/developer-access')
  })

  it.each([
    ['the document has no version', () => Promise.resolve({ data: {} }), TERMS_MISSING_MESSAGE],
    ['the document is not found', () => Promise.reject(httpError({ status: 404 })), TERMS_MISSING_MESSAGE],
    ['loading fails for another reason', () => Promise.reject(httpError({ status: 500 })), TERMS_LOAD_FAILED_MESSAGE]
  ])('shows an error and disables Agree when %s', async (_, response, message) => {
    getTermsOfService.mockImplementation(response)
    await mountAndLoad()

    expect(wrapper.find('[data-test="api-terms-load-error"]').text()).toBe(message)
    expect(agreeButton().attributes('disabled')).toBeDefined()
  })

  it('accepts the displayed version and returns to developer access to create a key', async () => {
    await mountAndLoad()

    await clickAgree()

    expect(acceptApiTerms).toHaveBeenCalledWith(123, 'k01')
    expect(router.push).toHaveBeenCalledWith({
      name: 'developer-access',
      params: { orgId: '123', openCreateKey: 'true' }
    })
    expect(wrapper.vm.isAccepting).toBe(false)
  })

  it.each([
    [
      'a newer version was published',
      httpError({ data: { code: 'API_TERMS_VERSION_MISMATCH' } }),
      'The API Terms of Use have been updated. Please refresh the page to review the latest version.'
    ],
    [
      'the terms are missing on the server',
      httpError({ data: { code: 'API_TERMS_NOT_FOUND' } }),
      TERMS_MISSING_MESSAGE
    ],
    ['accepting fails for another reason', new Error('network error'), 'The API Terms of Use could not be accepted. Please try again.']
  ])('shows an error and stays on the page when %s', async (_, error, message) => {
    acceptApiTerms.mockRejectedValue(error)
    await mountAndLoad()

    await clickAgree()

    expect(wrapper.find('[data-test="api-terms-accept-error"]').text()).toBe(message)
    expect(router.push).not.toHaveBeenCalled()
    expect(wrapper.vm.isAccepting).toBe(false)
  })

  it('clears a previous accept error when accepting again', async () => {
    acceptApiTerms.mockRejectedValueOnce(new Error('network error'))
    await mountAndLoad()

    await clickAgree()
    expect(wrapper.find('[data-test="api-terms-accept-error"]').exists()).toBe(true)

    await clickAgree()
    expect(wrapper.find('[data-test="api-terms-accept-error"]').exists()).toBe(false)
    expect(router.push).toHaveBeenCalled()
  })
})
