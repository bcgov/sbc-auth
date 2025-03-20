import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import SignoutView from '@/views/auth/SignoutView.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('SignoutView.vue', () => {
  let wrapper: Wrapper<SignoutView>
  const config = {
    'REGISTRY_HOME_URL': 'https://localhost:8080/'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()

    wrapper = mount(SignoutView, {
      localVue
    })

    vi.resetModules()
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })
})
