import { createLocalVue, mount } from '@vue/test-utils'
import StaffCreateAccountModal from '@/components/auth/staff/account-management/StaffCreateAccountModal.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(VueRouter)
Vue.use(Vuetify)
const vuetify = new Vuetify({})
const router = new VueRouter()

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('StaffCreateAccountModal.vue', () => {
  let wrapper: any
  let store: any
  const localVue = createLocalVue()
  localVue.use(Vuex)

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
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
