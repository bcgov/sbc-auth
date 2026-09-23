import { createLocalVue, mount } from '@vue/test-utils'
import ExistingAPIKeys from '@/components/auth/account-settings/advance-settings/ExistingAPIKeys.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
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

  const $t = () => 'test trans data'
  const apikeyList = {
    'consumer': {
      'consumerKey': consumerKey,
      'consumerStatus': 'approved'
    }
  }
  beforeEach(() => {
    const localVue = createLocalVue()

    const orgStore = useOrgStore()
    orgStore.getOrgApiKeys = vi.fn(() => {
      return apikeyList
    }) as any
    createOrgApiKey = vi.fn(() => Promise.resolve({}))
    orgStore.createOrgApiKey = createOrgApiKey as any
    orgStore.currentOrganization = {
      id: 123,
      name: 'test org'
    }

    wrapperFactory = (propsData) => {
      return mount(ExistingAPIKeys, {
        localVue,
        vuetify,
        mocks: { $t },
        propsData: {
          ...propsData
        },
        stubs: {
          'v-btn': {
            template: `<button @click='$listeners.click'></button>`
          },
          ModalDialog: true
        }
      })
    }

    wrapper = wrapperFactory({})
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

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
    wrapper.vm.$refs.createKeyModal = { open: vi.fn(), close: vi.fn() }
    wrapper.vm.$refs.createKeySuccessModal = { open: vi.fn(), close: vi.fn() }
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
    wrapper.vm.$refs.createKeyModal = { open: vi.fn(), close: vi.fn() }
    wrapper.vm.$refs.createKeySuccessModal = { open: vi.fn(), close: vi.fn() }
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
    wrapper.vm.$refs.createKeyModal = { open: vi.fn(), close: vi.fn() }
    wrapper.vm.$refs.createKeySuccessModal = { open: vi.fn(), close: vi.fn() }
    wrapper.vm.$refs.successDialog = { open: vi.fn(), close: vi.fn() }
    createOrgApiKey.mockResolvedValue({ consumer: { consumerKey: [] } })

    await wrapper.vm.onCreateKey({ apiKeyName: 'key1', environment: 'sandbox' })

    expect(wrapper.vm.alertTitle).toBe('API key has not been created')
    expect(wrapper.vm.generatedApiKey).toBe('')
    expect(wrapper.vm.$refs.createKeySuccessModal.open).not.toHaveBeenCalled()
    expect(wrapper.vm.$refs.successDialog.open).toHaveBeenCalled()
  })

  it('Should say the key was not created when the request fails', async () => {
    wrapper.vm.$refs.createKeyModal = { open: vi.fn(), close: vi.fn() }
    wrapper.vm.$refs.successDialog = { open: vi.fn(), close: vi.fn() }
    createOrgApiKey.mockRejectedValue(new Error('create failed'))

    await wrapper.vm.onCreateKey({ apiKeyName: 'key1', environment: 'sandbox' })

    expect(wrapper.vm.alertTitle).toBe('API key has not been created')
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
})
