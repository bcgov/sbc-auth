
import { createLocalVue, shallowMount } from '@vue/test-utils'

import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import GovmContactInfoForm from '@/components/auth/create-account/GovmContactInfoForm.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('GovmContactInfoForm.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(VueRouter)
    const userModule = {
      namespaced: true,
      state: {},
      actions: {
        getUserProfile: jest.fn()
      }

    }

    const router = new VueRouter()

    const store = new Vuex.Store({
      strict: false,
      modules: {
        user: userModule
      }
    })

    wrapperFactory = (propsData) => {
      return shallowMount(GovmContactInfoForm, {
        localVue,
        store,
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
    jest.resetModules()
    jest.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('renders the components properly and cancel button should be  shown', () => {
    expect(wrapper.find(GovmContactInfoForm).exists()).toBe(true)
    expect(wrapper.find(ConfirmCancelButton).exists()).toBe(true)
  })
})
