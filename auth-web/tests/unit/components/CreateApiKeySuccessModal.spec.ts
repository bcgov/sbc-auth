import { createLocalVue, mount } from '@vue/test-utils'
import CreateApiKeySuccessModal from '@/components/auth/account-settings/advance-settings/CreateApiKeySuccessModal.vue'
import { EventBus } from '@/event-bus'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('CreateApiKeySuccessModal.vue', () => {
  let wrapper: any

  beforeEach(() => {
    const localVue = createLocalVue()

    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined)
      }
    })

    wrapper = mount(CreateApiKeySuccessModal, {
      localVue,
      vuetify,
      propsData: {
        apiKey: 'test-api-key-123',
        environmentLabel: 'Sandbox'
      },
      stubs: {
        ModalDialog: true
      }
    })
  })

  afterEach(() => {
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('copies the api key to the clipboard', async () => {
    await wrapper.vm.copyApiKey()

    expect(navigator.clipboard.writeText).toBeCalledWith('test-api-key-123')
  })

  it('shows a toast after copying the api key', async () => {
    const emit = vi.spyOn(EventBus, '$emit')
    await wrapper.setProps({ apiKeyName: 'My Key' })
    await wrapper.vm.copyApiKey()

    expect(emit).toHaveBeenCalledWith('show-toast', { message: 'API key copied: My Key', type: 'default', timeout: 3000 })
  })

  it('does not show a toast when the copy fails', async () => {
    const emit = vi.spyOn(EventBus, '$emit')
    vi.spyOn(console, 'error').mockImplementation(() => {})
    navigator.clipboard.writeText = vi.fn().mockRejectedValue(new Error('denied'))
    await wrapper.vm.copyApiKey()

    expect(emit).not.toHaveBeenCalledWith('show-toast', expect.anything())
  })

  it('shows the key in full only once in the success modal', () => {
    const rendered = mount(CreateApiKeySuccessModal, {
      localVue: createLocalVue(),
      vuetify,
      propsData: {
        apiKey: 'mock-success-api-key',
        apiKeyName: 'My Key',
        environmentLabel: 'Sandbox'
      },
      stubs: {
        ModalDialog: {
          template: '<div><slot name="text" /><slot name="actions" /></div>'
        }
      }
    })

    expect(rendered.find('[data-test="created-key-row"]').text())
      .toContain('mock-success-api-key')
    expect(rendered.find('[data-test="created-key-summary"]').text()).toBe('My Key - Sandbox key')

    rendered.destroy()
  })
})
