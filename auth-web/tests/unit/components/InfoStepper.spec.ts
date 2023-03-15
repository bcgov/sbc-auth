import { createLocalVue, mount } from '@vue/test-utils'
import InfoStepper from '@/components/auth/home/InfoStepper.vue'
import Vue from 'vue'
import VueCompositionAPI from '@vue/composition-api'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

// @ts-ignore
Vue.use(VueCompositionAPI)
Vue.use(Vuetify)
Vue.use(VueRouter)

document.body.setAttribute('data-app', 'true')

describe('InfoStepper.vue', () => {
  let wrapper: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(VueRouter)

    const vuetify = new Vuetify({})
    const router = new VueRouter()

    const store = new Vuex.Store({
      strict: false
    })

    wrapper = mount(InfoStepper, {
      store,
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

    jest.resetModules()
    jest.clearAllMocks()
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
