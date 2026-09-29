import { createLocalVue, mount } from '@vue/test-utils'
import CreateApiKeyModal from '@/components/auth/account-settings/advance-settings/CreateApiKeyModal.vue'
import ExistingAPIKeys from '@/components/auth/account-settings/advance-settings/ExistingAPIKeys.vue'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'
import { useOrgStore } from '@/stores/org'

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')
const consumerKey = [
  {
    'apiAccess': [
      'ALL_API'
    ],
    'apiKey': 'mock-api-key-1234',
    'apiKeyName': 'key1',
    'environment': 'non-prod',
    'keyExpiryDate': 'never',
    'keyStatus': 'approved'
  }
]
describe('Account settings ExistingAPIKeys.vue', () => {
  let wrapper: any
  let wrapperFactory: any
  let createOrgApiKey: any
  let getApiTermsStatus: any
  let router: VueRouter

  const $t = () => 'test trans data'
  const apikeyList = {
    'consumer': {
      'consumerKey': consumerKey,
      'consumerStatus': 'approved'
    }
  }
  beforeEach(async () => {
    const localVue = createLocalVue()

    const orgStore = useOrgStore()
    orgStore.getOrgApiKeys = vi.fn(() => {
      return apikeyList
    }) as any
    createOrgApiKey = vi.fn(() => Promise.resolve({}))
    orgStore.createOrgApiKey = createOrgApiKey as any
    getApiTermsStatus = vi.fn(() => Promise.resolve({ isAccepted: true }))
    orgStore.getApiTermsStatus = getApiTermsStatus as any
    orgStore.currentOrganization = {
      id: 123,
      name: 'test org'
    }

    // params that aren't in the path are only kept when navigating to a named route
    wrapperFactory = async (routeParams = {}) => {
      router = new VueRouter({ routes: [{ name: 'developer-access', path: '/developer-access' }] })
      await router.push({ name: 'developer-access', params: routeParams })
      vi.spyOn(router, 'push').mockImplementation(() => Promise.resolve() as any)
      return mount(ExistingAPIKeys, {
        localVue,
        vuetify,
        router,
        mocks: { $t },
        stubs: {
          'v-btn': {
            template: `<button @click='$listeners.click'></button>`
          },
          ModalDialog: true
        }
      })
    }

    wrapper = await wrapperFactory()
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    vi.restoreAllMocks()
    wrapper.destroy()
  })

  // replace the modals so tests can check which ones were opened or closed
  function mockModals () {
    for (const ref of ['createKeyModal', 'createKeySuccessModal', 'successDialog']) {
      wrapper.vm.$refs[ref] = { open: vi.fn(), close: vi.fn() }
    }
  }

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the components properly', () => {
    expect(wrapper.find(ExistingAPIKeys).exists()).toBe(true)
  })

  it('renders proper header ', () => {
    expect(wrapper.find('h2').text()).toBe('Existing API Keys')
  })

  it('Should have data table', async () => {
    await wrapper.vm.loadApiKeys()
    expect(wrapper.find('.apikey-list')).toBeTruthy()
    expect(wrapper.find('[data-test="confirm-button-key1"]').exists()).toBe(true)
  })

  it('Should show Active status and revoke button for approved keys', async () => {
    await wrapper.vm.loadApiKeys()
    expect(wrapper.find('[data-test="key-status-chip"]').text()).toBe('Active')
    expect(wrapper.find('[data-test="confirm-button-key1"]').exists()).toBe(true)
  })

  it('Should show Revoked status and hide revoke button for revoked keys', async () => {
    wrapper.vm.apiKeyList = [{ ...consumerKey[0], keyStatus: 'revoked' }]
    await Vue.nextTick()
    expect(wrapper.find('[data-test="key-status-chip"]').text()).toBe('Revoked')
    expect(wrapper.find('[data-test="confirm-button-key1"]').exists()).toBe(false)
  })

  it('Should not send the environment when creating a key', async () => {
    await wrapper.vm.loadApiKeys()
    mockModals()
    createOrgApiKey.mockResolvedValue({
      consumer: {
        consumerKey: [
          { ...consumerKey[0], apiKey: 'new-key-value', environment: 'sandbox' }
        ]
      }
    })

    await wrapper.vm.onCreateKey({ apiKeyName: 'key1', environment: 'sandbox' })

    // the API gets the environment from the env the user logged into
    expect(createOrgApiKey).toHaveBeenCalledWith(123, { keyName: 'key1' })
    expect(wrapper.vm.generatedApiKey).toBe('new-key-value')
  })

  // Creating a key returns the single key that was generated
  const createdKey = {
    apiAccess: ['ALL_API'],
    apiKey: 'mock-api-key-ABCD',
    apiKeyName: 'test2',
    email: '1234-sandbox@dev.gov.bc.ca',
    environment: 'sandbox',
    keyExpiryDate: 'never',
    keyStatus: 'approved'
  }

  it('Should show the created key when the response is the created key in a list', async () => {
    await wrapper.vm.loadApiKeys()
    mockModals()
    // the create endpoint always wraps the created key(s) in consumer.consumerKey
    createOrgApiKey.mockResolvedValue({ consumer: { consumerKey: [createdKey] } })

    await wrapper.vm.onCreateKey({ apiKeyName: 'test2', environment: 'sandbox' })

    expect(wrapper.vm.generatedApiKey).toBe(createdKey.apiKey)
    expect(wrapper.vm.createdKeyEnvLabel).toBe('Sandbox')
    expect(wrapper.vm.$refs.createKeySuccessModal.open).toHaveBeenCalled()
    // the key is on screen as well, masked, and existing keys are preserved
    expect(wrapper.vm.apiKeyList.map((key: any) => key.apiKey)).toEqual([createdKey.apiKey, consumerKey[0].apiKey])
    expect(wrapper.vm.maskApiKey(createdKey.apiKey)).toBe('****ABCD')
  })

  it('Should not show an existing key when the response has no new key id', async () => {
    await wrapper.vm.loadApiKeys()
    mockModals()
    createOrgApiKey.mockResolvedValue({ consumer: { consumerKey: [] } })

    await wrapper.vm.onCreateKey({ apiKeyName: 'key1', environment: 'sandbox' })

    expect(wrapper.vm.alertTitle).toBe('API key has not been created')
    expect(wrapper.vm.generatedApiKey).toBe('')
    expect(wrapper.vm.$refs.createKeySuccessModal.open).not.toHaveBeenCalled()
    expect(wrapper.vm.$refs.successDialog.open).toHaveBeenCalled()
  })

  it('Should say the key was not created when the request fails', async () => {
    mockModals()
    createOrgApiKey.mockRejectedValue(new Error('create failed'))

    await wrapper.vm.onCreateKey({ apiKeyName: 'key1', environment: 'sandbox' })

    expect(wrapper.vm.alertTitle).toBe('API key has not been created')
    expect(wrapper.vm.alertText).toBe('')
    expect(wrapper.vm.$refs.successDialog.open).toHaveBeenCalled()
  })

  it('Should open Confirmation modal on revoke button click', async () => {
    await wrapper.vm.loadApiKeys()
    const stub = vi.fn(() => consumerKey)
    wrapper.setMethods({ confirmationModal: stub })

    wrapper.find('[data-test="confirm-button-key1"]').trigger('click')
    await Vue.nextTick()
    await Vue.nextTick()

    expect(wrapper.vm.confirmationModal).toBeCalled()
    expect(wrapper.find("[data-test='confirmation-modal']").exists()).toBe(true)
  })

  const apiTermsRoute = { name: 'api-terms-of-use', params: { orgId: '123' } }

  describe('with creating API keys enabled', () => {
    beforeEach(async () => {
      vi.spyOn(LaunchDarklyService, 'getFlag').mockReturnValue(true)
      wrapper.destroy()
      wrapper = await wrapperFactory()
      await flushPromises()
      mockModals()
    })

    async function clickCreateKey () {
      wrapper.find('[data-test="create-api-key-button"]').trigger('click')
      await flushPromises()
    }

    it('Should open the create key dialog when the latest API terms are accepted', async () => {
      await clickCreateKey()

      expect(getApiTermsStatus).toHaveBeenCalledWith(123)
      expect(wrapper.vm.$refs.createKeyModal.open).toHaveBeenCalled()
      expect(router.push).not.toHaveBeenCalled()
    })

    it.each([
      ['the latest API terms are not accepted', () => Promise.resolve({ isAccepted: false })],
      ['the terms status can not be loaded', () => Promise.reject(new Error('status failed'))]
    ])('Should go to the API terms page when %s', async (_, status) => {
      getApiTermsStatus.mockImplementation(status)

      await clickCreateKey()

      expect(wrapper.vm.$refs.createKeyModal.open).not.toHaveBeenCalled()
      expect(router.push).toHaveBeenCalledWith(apiTermsRoute)
    })
  })

  it('Should go to the API terms page when creating a key fails because the terms are not accepted', async () => {
    mockModals()
    createOrgApiKey.mockRejectedValue({ response: { data: { code: 'API_TERMS_NOT_ACCEPTED' } } })

    await wrapper.vm.onCreateKey({ apiKeyName: 'key1', environment: 'sandbox' })

    expect(wrapper.vm.$refs.createKeyModal.close).toHaveBeenCalled()
    expect(router.push).toHaveBeenCalledWith(apiTermsRoute)
    expect(wrapper.vm.$refs.successDialog.open).not.toHaveBeenCalled()
  })

  it('Should show the error message when creating a key fails because the terms are missing', async () => {
    const message = 'API Terms of Use are missing. API keys cannot be created until they are available.'
    mockModals()
    createOrgApiKey.mockRejectedValue({ response: { data: { code: 'API_TERMS_NOT_FOUND', message } } })

    await wrapper.vm.onCreateKey({ apiKeyName: 'key1', environment: 'sandbox' })

    expect(wrapper.vm.alertTitle).toBe('API key has not been created')
    expect(wrapper.vm.alertText).toBe(message)
    expect(wrapper.vm.$refs.successDialog.open).toHaveBeenCalled()
    expect(router.push).not.toHaveBeenCalled()
  })

  // the terms page routes back with openCreateKey after the terms are accepted
  it.each([
    [true, { openCreateKey: 'true' }, true],
    [true, {}, false],
    [false, { openCreateKey: 'true' }, false]
  ])('With creating keys enabled %s and route params %j, the create key dialog opens on load: %s',
    async (enabled, routeParams, opens) => {
      vi.spyOn(LaunchDarklyService, 'getFlag').mockReturnValue(enabled)
      const openModal = vi.spyOn((CreateApiKeyModal as any).options.methods, 'open').mockImplementation(() => {})
      wrapper.destroy()
      wrapper = await wrapperFactory(routeParams)
      await flushPromises()

      expect(openModal).toHaveBeenCalledTimes(opens ? 1 : 0)
    })
})
