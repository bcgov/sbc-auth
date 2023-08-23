import { createLocalVue, shallowMount } from '@vue/test-utils'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import GovmContactInfoForm from '@/components/auth/create-account/GovmContactInfoForm.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('GovmContactInfoForm.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    const router = new VueRouter()
    wrapperFactory = (propsData) => {
      return shallowMount(GovmContactInfoForm, {
        localVue,
        router,
        vuetify,
        propsData: {
          ...propsData
        }
      })
    }

    wrapper = wrapperFactory()
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the components properly and cancel button should be  shown', () => {
    expect(wrapper.findComponent(GovmContactInfoForm).exists()).toBe(true)
    expect(wrapper.findComponent(ConfirmCancelButton).exists()).toBe(true)
  })
})
