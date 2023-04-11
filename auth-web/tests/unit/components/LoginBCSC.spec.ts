import { createLocalVue, mount } from '@vue/test-utils'
import LoginBCSC from '@/components/auth/home/LoginBCSC.vue'
import Vue from 'vue'
import VueCompositionAPI from '@vue/composition-api'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

// @ts-ignore
Vue.use(VueCompositionAPI)
Vue.use(VueRouter)
Vue.use(Vuetify)
document.body.setAttribute('data-app', 'true')

describe('LoginBCSC.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(VueRouter)

    const router = new VueRouter()
    const store = new Vuex.Store({})
    const vuetify = new Vuetify({})

    wrapperFactory = (slotsData) => {
      return mount(LoginBCSC, {
        router,
        store,
        vuetify,
        localVue,
        slots: {
          ...slotsData
        }
      })
    }

    wrapper = wrapperFactory({})
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('it renders correctly with default slot', () => {
    expect(wrapper.find('.v-card__title').text()).toBe('Create a BC Registries Account')
    expect(wrapper.find('.font-weight-bold').text()).toBe('Log in')
  })

  it('it renders slot', () => {
    wrapper = wrapperFactory({ actions: '<div>Action</div>' })
    expect(wrapper.html()).toContain('<div>Action</div>')
  })
})
