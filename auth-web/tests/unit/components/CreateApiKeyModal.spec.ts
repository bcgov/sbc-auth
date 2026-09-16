import { createLocalVue, mount } from '@vue/test-utils'
import CreateApiKeyModal from '@/components/auth/account-settings/advance-settings/CreateApiKeyModal.vue'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('CreateApiKeyModal.vue', () => {
  let wrapper: any

  beforeEach(() => {
    const localVue = createLocalVue()

    wrapper = mount(CreateApiKeyModal, {
      localVue,
      vuetify,
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

  it('emits create event with the entered name and environment on valid submission', async () => {
    wrapper.vm.newKeyName = 'My Key'
    wrapper.vm.newKeyEnvironment = 'sandbox'

    wrapper.vm.createKey()

    expect(wrapper.emitted('create')).toBeTruthy()
    expect(wrapper.emitted('create')[0][0]).toEqual({
      apiKeyName: 'My Key',
      environment: 'sandbox'
    })
  })
})
