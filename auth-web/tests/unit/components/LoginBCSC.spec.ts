import { createLocalVue, mount } from '@vue/test-utils'
import LoginBCSC from '@/components/auth/home/LoginBCSC.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import vueCompositionApi from '@vue/composition-api'

Vue.use(VueRouter)
Vue.use(Vuetify)
Vue.use(vueCompositionApi)
document.body.setAttribute('data-app', 'true')

describe('LoginBCSC.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(VueRouter)
    localVue.use(vueCompositionApi)

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
    expect(wrapper.isVueInstance()).toBeTruthy()
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
