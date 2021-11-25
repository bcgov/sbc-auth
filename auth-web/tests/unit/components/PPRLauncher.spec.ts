import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import PPRLauncher from '@/components/auth/staff/PPRLauncher.vue'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)
Vue.use(VueI18n)

describe('PPRLauncher.vue', () => {
  let wrapper: Wrapper<any>
  const title = 'Staff Personal Property Registry'
  const text = 'Register or search for legal claims on personal property.'
  const pprUrl = 'ppr-web'
  const config = {
    'PPR_WEB_URL': pprUrl
  }
  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const vuetify = new Vuetify({})

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {}
    })
    const $t = (val: string) => {
      if (val === 'pprLauncherTitle') return title
      if (val === 'pprLauncherText') return text
      return ''
    }
    wrapper = mount(PPRLauncher, {
      store,
      localVue,
      vuetify,
      mocks: { $t }
    })
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('renders img, title, text and button', () => {
    expect(wrapper.find('.product-container').exists()).toBe(true)
    expect(wrapper.find('.product-img').exists()).toBe(true)
    expect(wrapper.find('.product-info').exists()).toBe(true)
    expect(wrapper.find('.product-info h2').text()).toBe('Staff Personal Property Registry')
    expect(wrapper.find('.product-info p').text()).toContain('claims on personal property.')
    expect(wrapper.find('.action-btn').exists()).toBe(true)
    expect(wrapper.find('.action-btn').text()).toContain('Open')
    expect(wrapper.vm.pprUrl).toEqual(pprUrl)
  })
})
