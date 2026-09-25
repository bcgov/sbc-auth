import { createLocalVue, mount } from '@vue/test-utils'
import CreateApiKeySuccessModal from '@/components/auth/account-settings/advance-settings/CreateApiKeySuccessModal.vue'
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

  it('shows the key in full only once in the success modal', () => {
    const rendered = mount(CreateApiKeySuccessModal, {
      localVue: createLocalVue(),
      vuetify,
      propsData: {
        apiKey: 'mock-success-api-key',
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
    expect(rendered.find('[data-test="created-key-summary"]').text()).toBe('Sandbox key')

    rendered.destroy()
  })
})
