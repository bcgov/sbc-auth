import { createLocalVue, mount } from '@vue/test-utils'
import StaffCreateAccountModal from '@/components/auth/staff/account-management/StaffCreateAccountModal.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})
const router = new VueRouter()

describe('StaffCreateAccountModal.vue', () => {
  let wrapper: any
  let store: any
  const localVue = createLocalVue()

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('Should have a Modal', () => {
    wrapper = mount(StaffCreateAccountModal, {
      store,
      vuetify,
      localVue,
      router,

      mocks: {
        $t: (mock) => mock
      }
    })

    expect(wrapper.vm).toBeTruthy()
    expect(wrapper.find('[data-test="create-account-modal"]')).toBeTruthy()
  })
})
