import { createLocalVue, mount } from '@vue/test-utils'
import InfoStepper from '@/components/auth/home/InfoStepper.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

document.body.setAttribute('data-app', 'true')

describe('InfoStepper.vue', () => {
  let wrapper: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(VueRouter)

    const vuetify = new Vuetify({})
    const router = new VueRouter()

    wrapper = mount(InfoStepper, {
      router,
      localVue,
      vuetify,
      mocks: {
        $route: {
          params: {
            id: 'id'
          }
        },
        $router: {
          params: {
            id: 'id'
          }
        }
      }
    })

    vi.resetModules()
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('is renders correctly', () => {
    expect(wrapper.find('.next-step-wrapper').exists()).toBe(true)
    expect(wrapper.find('#step-buttons-container').exists()).toBe(true)
    expect(wrapper.find('.next-step-btn').exists()).toBe(true)
    expect(wrapper.find('.step').exists()).toBe(true)
  })

  it('renders correct number of steps', () => {
    expect(wrapper.findAll('.step').length).toBe(4)
  })
})
