import { createLocalVue, mount } from '@vue/test-utils'
import RestrictedProductView from '@/views/auth/RestrictedProductView.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('RestrictedProductView.vue', () => {
  let wrapper: any

  beforeEach(() => {
    const localVue = createLocalVue()
    const router = new VueRouter()
    wrapper = mount(RestrictedProductView, {
      localVue,
      router,
      vuetify,
      mocks: {
        $t: () => 'Restricted Access'
      }
    })
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('RestrictedProductView is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })
  it('RestrictedProductView contains the messages', () => {
    const requestBtn = wrapper.find('.btn-request-access')
    expect(requestBtn).toBeDefined()
    expect(requestBtn.text()).toContain('Request Access')
    expect(wrapper.find('h1').text()).toBe('Restricted Access')
  })
})
