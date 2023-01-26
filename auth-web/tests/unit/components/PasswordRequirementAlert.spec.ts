import { createLocalVue, mount } from '@vue/test-utils'
import PasswordRequirementAlert from '@/components/auth/common/PasswordRequirementAlert.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('PasswordRequirementAlert.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({})

    wrapperFactory = (propsData) => {
      return mount(PasswordRequirementAlert, {
        localVue,
        store,
        vuetify
      })
    }

    wrapper = wrapperFactory({ PasswordRequirementAlert: {} })
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('renders the components properly', () => {
    expect(wrapper.find(PasswordRequirementAlert).exists()).toBe(true)
  })

  it('renders the v-alert properly', () => {
    const alert = wrapper.vm.$el.querySelectorAll('.v-alert')
    const lists = wrapper.vm.$el.querySelectorAll('li')
    expect(lists.length).toStrictEqual(4)
    expect(alert.length).toStrictEqual(1)
  })
})
