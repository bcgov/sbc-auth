
import { createLocalVue, shallowMount } from '@vue/test-utils'
import GLPaymentForm from '@/components/auth/common/GLPaymentForm.vue'
import GovmPaymentMethodSelector from '@/components/auth/create-account/GovmPaymentMethodSelector.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('GovmPaymentMethodSelector.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    const router = new VueRouter()

    wrapperFactory = (propsData) => {
      return shallowMount(GovmPaymentMethodSelector, {
        localVue,
        router,
        vuetify,
        propsData: {
          ...propsData
        }
      })
    }

    wrapper = wrapperFactory({ userProfile: {} })
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the components properly and GLPaymentForm should be  shown', () => {
    expect(wrapper.findComponent(GovmPaymentMethodSelector).exists()).toBe(true)
    expect(wrapper.findComponent(GLPaymentForm).exists()).toBe(true)
    // expect(wrapper.find('.save-continue-button').is('[disabled]')).toBe(true)
  })
})
