import { createLocalVue, mount } from '@vue/test-utils'
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
    },
    'maxNamedKeys': 10
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

    // the new table is shown by default, legacy table tests turn the flag off
    vi.spyOn(LaunchDarklyService, 'getFlag').mockReturnValue(true)
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
    for (const ref of ['createKeySuccessModal', 'successDialog', 'revokeSuccessDialog']) {
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
    expect(wrapper.find('h2').text()).toBe('API Keys')
  })

  const namedKeys = (count: number) => Array.from({ length: count }, (_, i) => ({
    ...consumerKey[0], apiKey: `named-key-${i}`, apiKeyName: `named${i}`
  }))
  const unnamedKeys = (names: any[]) => names.map((apiKeyName, i) => ({
    ...consumerKey[0], apiKey: `unnamed-key-${i}`, apiKeyName
  }))
  const keyCounts = () => wrapper.find('[data-test="api-key-counts"]').text().replace(/\s+/g, ' ')

  it('Should show the named and unnamed key counts, including revoked keys', async () => {
    wrapper.vm.apiKeyList = [
      ...namedKeys(2),
      { ...consumerKey[0], apiKey: 'revoked-key', keyStatus: 'revoked' },
      ...unnamedKeys(['', '  ', null, undefined])
    ]
    await Vue.nextTick()

    expect(keyCounts()).toBe('3/10 Named Keys | 4 Unnamed Keys')
  })

  it('Should update the key counts when a key is created', async () => {
    await wrapper.vm.loadApiKeys()
    await Vue.nextTick()
    expect(keyCounts()).toBe('1/10 Named Keys | 0 Unnamed Keys')
    mockModals()
    createOrgApiKey.mockResolvedValue({
      consumer: { consumerKey: [{ ...consumerKey[0], apiKey: 'new-key-value', apiKeyName: 'key2' }] }
    })

    await wrapper.vm.onCreateKey({ apiKeyName: 'key2' })
    await Vue.nextTick()

    expect(keyCounts()).toBe('2/10 Named Keys | 0 Unnamed Keys')
  })

  it('Should have data table', async () => {
    await wrapper.vm.loadApiKeys()
    expect(wrapper.find('.apikey-list')).toBeTruthy()
    expect(wrapper.find('[data-test="confirm-button-mock-api-key-1234"]').exists()).toBe(true)
  })

  // create API key feature flag switches between the legacy and the new table
  async function mountWithCreateApiKeyFF (featureFlagEnabled: boolean) {
    vi.spyOn(LaunchDarklyService, 'getFlag').mockReturnValue(featureFlagEnabled)
    wrapper.destroy()
    wrapper = await wrapperFactory()
    await flushPromises()
  }

  // legacy table - feature flag off
  it('Should show the legacy table when creating API keys is disabled', async () => {
    await mountWithCreateApiKeyFF(false)
    const tableHeaders = wrapper.findAll('.apikey-list th').wrappers.map((th: any) => th.text())
    expect(tableHeaders).toEqual(['Name', 'Environment', 'API Key', 'Actions'])
    expect(wrapper.find('[data-test="key-status-chip"]').exists()).toBe(false)
    expect(wrapper.find('[data-test="create-api-key-button"]').exists()).toBe(false)
  })

  // legacy table - feature flag off
  it('Should show the full API key when creating API keys is disabled', async () => {
    await mountWithCreateApiKeyFF(false)
    expect(wrapper.find('.apikey-list tbody').text()).toContain(consumerKey[0].apiKey)
  })

  // new table - feature flag on
  it('Should show Active status and revoke button for approved keys', async () => {
    await mountWithCreateApiKeyFF(true)
    expect(wrapper.find('[data-test="key-status-chip"]').text()).toBe('Active')
    expect(wrapper.find('[data-test="confirm-button-mock-api-key-1234"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="delete-button-mock-api-key-1234"]').exists()).toBe(false)
  })

  // new table - feature flag on
  it('Should show Revoked status and hide revoke button for revoked keys', async () => {
    await mountWithCreateApiKeyFF(true)
    wrapper.vm.apiKeyList = [{ ...consumerKey[0], keyStatus: 'revoked' }]
    await Vue.nextTick()
    expect(wrapper.find('[data-test="key-status-chip"]').text()).toBe('Revoked')
    expect(wrapper.find('[data-test="confirm-button-mock-api-key-1234"]').exists()).toBe(false)
    expect(wrapper.find('[data-test="delete-button-mock-api-key-1234"]').exists()).toBe(true)
  })

  it('Should show other statuses as is with no revoke or delete button', async () => {
    wrapper.vm.apiKeyList = [{ ...consumerKey[0], keyStatus: 'pending' }]
    await Vue.nextTick()
    expect(wrapper.find('[data-test="key-status-chip"]').text()).toBe('Pending')
    expect(wrapper.find('[data-test="confirm-button-mock-api-key-1234"]').exists()).toBe(false)
    expect(wrapper.find('[data-test="delete-button-mock-api-key-1234"]').exists()).toBe(false)
  })

  it('Should open the confirmation modal for a delete on delete button click', async () => {
    wrapper.vm.apiKeyList = [{ ...consumerKey[0], keyStatus: 'revoked' }]
    await Vue.nextTick()
    wrapper.vm.$refs.confirmDeleteDialog = { open: vi.fn() }

    wrapper.find('[data-test="delete-button-mock-api-key-1234"]').trigger('click')
    await Vue.nextTick()

    expect(wrapper.vm.selectedApi.apiKey).toBe('mock-api-key-1234')
    expect(wrapper.vm.$refs.confirmDeleteDialog.open).toHaveBeenCalled()
  })

  it.each(['confirm-revoke-key-button', 'confirm-delete-key-button'])(
    'Should disable %s while the key action is running', async (dataTest) => {
      wrapper.vm.isLoading = true
      await Vue.nextTick()
      const button = wrapper.find(`[data-test="${dataTest}"]`)

      expect(button.exists()).toBe(true)
      expect(button.attributes('disabled')).toBeTruthy()
    }
  )

  it('Should delete the key and reload all keys', async () => {
    const orgStore = useOrgStore()
    orgStore.deleteOrgApiKey = vi.fn(() => Promise.resolve({})) as any
    orgStore.revokeOrgApiKeys = vi.fn(() => Promise.resolve({})) as any
    wrapper.vm.$refs.confirmDeleteDialog = { close: vi.fn() }
    wrapper.vm.$refs.successDialog = { open: vi.fn() }
    wrapper.vm.selectedApi = { ...consumerKey[0], keyStatus: 'revoked' }
    vi.mocked(orgStore.getOrgApiKeys).mockClear()

    await wrapper.vm.deleteApi()

    expect(orgStore.deleteOrgApiKey).toHaveBeenCalledWith({ orgId: 123, apiKey: 'mock-api-key-1234' })
    expect(orgStore.revokeOrgApiKeys).not.toHaveBeenCalled()
    expect(orgStore.getOrgApiKeys).toHaveBeenCalledWith(123, true)
    expect(wrapper.vm.alertTitle).toBe('API key has been Deleted')
    expect(wrapper.vm.$refs.confirmDeleteDialog.close).toHaveBeenCalled()
  })

  it('Should load all keys, including revoked ones', async () => {
    const getOrgApiKeys = useOrgStore().getOrgApiKeys as any
    await wrapper.vm.loadApiKeys()
    expect(getOrgApiKeys).toHaveBeenLastCalledWith(123, true)
  })

  it('Should reload all keys and show the revoke success modal after a revoke', async () => {
    const orgStore = useOrgStore()
    orgStore.revokeOrgApiKeys = vi.fn(() => Promise.resolve({})) as any
    wrapper.vm.$refs.confirmActionDialog = { close: vi.fn() }
    mockModals()
    wrapper.vm.selectedApi = consumerKey[0]
    vi.mocked(orgStore.getOrgApiKeys).mockClear()

    await wrapper.vm.revokeApi()

    expect(orgStore.revokeOrgApiKeys).toHaveBeenCalledWith({ orgId: 123, apiKey: 'mock-api-key-1234' })
    expect(orgStore.getOrgApiKeys).toHaveBeenCalledWith(123, true)
    expect(wrapper.vm.$refs.confirmActionDialog.close).toHaveBeenCalled()
    expect(wrapper.vm.revokedKeyName).toBe('key1')
    expect(wrapper.vm.$refs.revokeSuccessDialog.open).toHaveBeenCalled()
    expect(wrapper.vm.$refs.successDialog.open).not.toHaveBeenCalled()
  })

  it('Should show the alert modal instead of the revoke success modal when a revoke fails', async () => {
    const orgStore = useOrgStore()
    orgStore.revokeOrgApiKeys = vi.fn(() => Promise.reject(new Error('revoke failed'))) as any
    wrapper.vm.$refs.confirmActionDialog = { close: vi.fn() }
    mockModals()
    wrapper.vm.selectedApi = consumerKey[0]

    await wrapper.vm.revokeApi()

    expect(wrapper.vm.alertTitle).toBe('API key has not been Revoked')
    expect(wrapper.vm.$refs.successDialog.open).toHaveBeenCalled()
    expect(wrapper.vm.$refs.revokeSuccessDialog.open).not.toHaveBeenCalled()
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
    expect(createOrgApiKey).toHaveBeenCalledWith(123, { apiKeyName: 'key1' })
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

  it('Should reload the keys and say the key was created when the response has no new key', async () => {
    await wrapper.vm.loadApiKeys()
    mockModals()
    createOrgApiKey.mockResolvedValue({ consumer: { consumerKey: [] } })
    const getOrgApiKeys = useOrgStore().getOrgApiKeys as any
    getOrgApiKeys.mockClear()

    await wrapper.vm.onCreateKey({ apiKeyName: 'key1', environment: 'sandbox' })

    expect(getOrgApiKeys).toHaveBeenCalledWith(123, true)
    expect(wrapper.vm.alertTitle).toBe('API key has been created')
    expect(wrapper.vm.alertText).toContain('could not be displayed')
    expect(wrapper.vm.notificationColor).toBe('warning')
    expect(wrapper.vm.generatedApiKey).toBe('')
    expect(wrapper.vm.isCreateFormOpen).toBe(false)
    expect(wrapper.vm.isCreating).toBe(false)
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

    wrapper.find('[data-test="confirm-button-mock-api-key-1234"]').trigger('click')
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

    it('Should open the create key form when the latest API terms are accepted', async () => {
      await clickCreateKey()

      expect(getApiTermsStatus).toHaveBeenCalledWith(123)
      expect(wrapper.vm.isCreateFormOpen).toBe(true)
      expect(router.push).not.toHaveBeenCalled()
    })

    const createKeyButton = () => wrapper.find('[data-test="create-api-key-button"]')
    const limitNotice = () => wrapper.find('[data-test="named-key-limit-notice"]')

    it('Should show the limit notice instead of the form when the named key limit is reached', async () => {
      wrapper.vm.apiKeyList = namedKeys(10)
      await Vue.nextTick()
      // the button stays clickable until the notice is shown
      expect(createKeyButton().attributes('disabled')).toBeFalsy()
      expect(limitNotice().exists()).toBe(false)

      await clickCreateKey()

      expect(getApiTermsStatus).toHaveBeenCalledWith(123)
      expect(wrapper.vm.isCreateFormOpen).toBe(false)
      expect(limitNotice().text()).toContain('You have reached the maximum of 10 named API keys.')
      expect(createKeyButton().attributes('disabled')).toBeTruthy()
    })

    it('Should hide the limit notice and enable the button again on cancel', async () => {
      wrapper.vm.apiKeyList = namedKeys(10)
      await clickCreateKey()

      wrapper.find('[data-test="cancel-unnamed-key-button"]').trigger('click')
      await Vue.nextTick()

      expect(limitNotice().exists()).toBe(false)
      expect(createKeyButton().attributes('disabled')).toBeFalsy()
      expect(createOrgApiKey).not.toHaveBeenCalled()
    })

    it('Should create an unnamed key from the limit notice', async () => {
      wrapper.vm.apiKeyList = namedKeys(10)
      await clickCreateKey()
      createOrgApiKey.mockResolvedValue({
        consumer: { consumerKey: [{ ...consumerKey[0], apiKey: 'unnamed-key-value', apiKeyName: '' }] }
      })

      wrapper.find('[data-test="create-unnamed-key-button"]').trigger('click')
      await flushPromises()

      expect(createOrgApiKey).toHaveBeenCalledWith(123, { apiKeyName: undefined })
      expect(wrapper.vm.$refs.createKeySuccessModal.open).toHaveBeenCalled()
      expect(keyCounts()).toBe('10/10 Named Keys | 1 Unnamed Keys')
      expect(limitNotice().exists()).toBe(false)
      expect(createKeyButton().attributes('disabled')).toBeFalsy()
    })

    it('Should hide the limit notice when a named key is removed', async () => {
      wrapper.vm.apiKeyList = namedKeys(10)
      await clickCreateKey()

      wrapper.vm.apiKeyList = namedKeys(9)
      await Vue.nextTick()

      expect(limitNotice().exists()).toBe(false)
      expect(createKeyButton().attributes('disabled')).toBeFalsy()
    })

    it('Should not count unnamed keys towards the named key limit', async () => {
      wrapper.vm.apiKeyList = [...namedKeys(9), ...unnamedKeys(['', null, ''])]
      await Vue.nextTick()

      expect(wrapper.find('[data-test="create-api-key-button"]').attributes('disabled')).toBeFalsy()
      await clickCreateKey()

      expect(wrapper.vm.isCreateFormOpen).toBe(true)
    })

    it.each([
      ['the latest API terms are not accepted', () => Promise.resolve({ isAccepted: false })],
      ['the terms status can not be loaded', () => Promise.reject(new Error('status failed'))]
    ])('Should go to the API terms page when %s', async (_, status) => {
      getApiTermsStatus.mockImplementation(status)

      await clickCreateKey()

      expect(wrapper.vm.isCreateFormOpen).toBe(false)
      expect(router.push).toHaveBeenCalledWith(apiTermsRoute)
    })
  })

  it('Should go to the API terms page when creating a key fails because the terms are not accepted', async () => {
    mockModals()
    createOrgApiKey.mockRejectedValue({ response: { data: { code: 'API_TERMS_NOT_ACCEPTED' } } })

    await wrapper.vm.onCreateKey({ apiKeyName: 'key1', environment: 'sandbox' })

    expect(wrapper.vm.isCreateFormOpen).toBe(false)
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
  ])('With creating keys enabled %s and route params %j, the create key form opens on load: %s',
    async (enabled, routeParams, opens) => {
      vi.spyOn(LaunchDarklyService, 'getFlag').mockReturnValue(enabled)
      wrapper.destroy()
      wrapper = await wrapperFactory(routeParams)
      await flushPromises()

      expect(wrapper.vm.isCreateFormOpen).toBe(opens)
    })

  it('Should sort by created date, newest first by default', async () => {
    wrapper.vm.apiKeyList = [1, 2, 3].map(day => ({
      ...consumerKey[0],
      apiKey: `api-key-${day}`,
      apiKeyName: `key${day}`,
      keyCreatedDate: `2026-01-0${day}T00:00:00`
    }))
    await Vue.nextTick()

    const names = wrapper.findAll('tbody tr .font-weight-bold').wrappers.map(r => r.text())
    expect(names).toEqual(['key3', 'key2', 'key1'])
  })

  it('Should show a new key on the first page when the create response has no created date', async () => {
    mockModals()
    wrapper.vm.apiKeyList = [1, 2, 3, 4, 5, 6].map(day => ({
      ...consumerKey[0],
      apiKey: `api-key-${day}`,
      apiKeyName: `key${day}`,
      keyCreatedDate: `2026-01-0${day}T00:00:00`
    }))
    createOrgApiKey.mockResolvedValue({
      consumer: { consumerKey: [{ apiKey: 'new-key-value', apiKeyName: 'new key', keyStatus: 'approved' }] }
    })

    await wrapper.vm.onCreateKey({ apiKeyName: 'new key' })
    await Vue.nextTick()

    const names = wrapper.findAll('tbody tr .font-weight-bold').wrappers.map(r => r.text())
    expect(names[0]).toBe('new key')
    expect(wrapper.find('[data-test="new-api-key-chip"]').exists()).toBe(true)
  })

  it('Should give each row its own action button tag', async () => {
    wrapper.vm.apiKeyList = [1, 2].map(day => ({ ...consumerKey[0], apiKey: `api-key-${day}`, apiKeyName: '' }))
    await Vue.nextTick()

    expect(wrapper.find('[data-test="confirm-button-api-key-1"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="confirm-button-api-key-2"]').exists()).toBe(true)
  })

  describe('when the named key limit is reached on create', () => {
    const message = 'You have reached the maximum of 10 named API keys.'
    const namedKeys = Array.from({ length: 10 }, (_, i) => ({ ...consumerKey[0], apiKey: `key-${i}`, apiKeyName: `k${i}` }))

    beforeEach(() => {
      mockModals()
      createOrgApiKey.mockRejectedValue({ response: { data: { code: 'API_KEY_NAMED_LIMIT_REACHED', message } } })
    })

    it('Should reload the keys and show the create unnamed key notice', async () => {
      vi.mocked(useOrgStore().getOrgApiKeys).mockReturnValueOnce({ consumer: { consumerKey: namedKeys }, maxNamedKeys: 10 })

      await wrapper.vm.onCreateKey({ apiKeyName: 'key11' })
      await Vue.nextTick()

      expect(wrapper.find('[data-test="named-key-limit-notice"]').exists()).toBe(true)
      expect(wrapper.vm.$refs.successDialog.open).not.toHaveBeenCalled()
    })

    it('Should show the error message when the limit is unknown', async () => {
      vi.mocked(useOrgStore().getOrgApiKeys).mockReturnValueOnce({ consumer: { consumerKey: namedKeys } })

      await wrapper.vm.onCreateKey({ apiKeyName: 'key11' })

      expect(wrapper.vm.alertText).toBe(message)
      expect(wrapper.vm.$refs.successDialog.open).toHaveBeenCalled()
    })
  })

  it('Should show the error message when deleting a key that is not revoked', async () => {
    const message = 'API key must be revoked before it can be deleted.'
    const orgStore = useOrgStore()
    orgStore.deleteOrgApiKey = vi.fn().mockRejectedValue({ response: { data: { code: 'API_KEY_NOT_REVOKED', message } } }) as any
    wrapper.vm.$refs.confirmDeleteDialog = { close: vi.fn() }
    wrapper.vm.$refs.successDialog = { open: vi.fn() }
    wrapper.vm.selectedApi = { ...consumerKey[0] }

    await wrapper.vm.deleteApi()

    expect(wrapper.vm.alertTitle).toBe('API key has not been Deleted')
    expect(wrapper.vm.alertText).toBe(message)
    expect(wrapper.vm.$refs.successDialog.open).toHaveBeenCalled()
  })
})
