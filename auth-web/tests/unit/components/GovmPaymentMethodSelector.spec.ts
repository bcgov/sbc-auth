
import { createLocalVue, shallowMount } from '@vue/test-utils'
import GLPaymentForm from '@/components/auth/common/GLPaymentForm.vue'
import GovmPaymentMethodSelector from '@/components/auth/create-account/GovmPaymentMethodSelector.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('GovmPaymentMethodSelector.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(VueRouter)
    const router = new VueRouter()

    const store = new Vuex.Store({
      strict: false,
      modules: {}
    })

    wrapperFactory = (propsData) => {
      return shallowMount(GovmPaymentMethodSelector, {
        localVue,
        store,
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
    jest.resetModules()
    jest.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('renders the components properly and GLPaymentForm should be  shown', () => {
    expect(wrapper.find(GovmPaymentMethodSelector).exists()).toBe(true)
    expect(wrapper.find(GLPaymentForm).exists()).toBe(true)
    // expect(wrapper.find('.save-continue-button').is('[disabled]')).toBe(true)
  })
})
