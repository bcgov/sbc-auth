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
  const assetLauncherText = 'Register or search for manufactured homes and register or search for legal claims on ' +
      'personal property.'
  const assetLauncherTitle = 'Staff Asset Registries'
  const pprLauncherText = 'Register or search for legal claims on personal property.'
  const pprLauncherTitle = 'Staff Personal Property Registry'
  const mhrLauncherText = 'Register or search for legal claims on manufactured homes.'
  const mhrLauncherTitle = 'Staff Manufactured Home Registry'

  const pprUrl = 'https://dev.assets.bcregistry.gov.bc.ca/'
  const config = {
    'PPR_WEB_URL': pprUrl
  }
  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  let userModule = {
    namespaced: true,
    state: {
      currentUser: {
        fullName: 'user2',
        roles: ['ppr']
      }
    }
  }

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    const vuetify = new Vuetify({})

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: { user: userModule }
    })

    const $t = (val: string) => {
      switch (val) {
        case 'pprLauncherTitle': return pprLauncherTitle
        case 'pprLauncherText': return pprLauncherText
        case 'mhrLauncherTitle': return mhrLauncherTitle
        case 'mhrLauncherText': return mhrLauncherText
        case 'assetLauncherTitle': return assetLauncherTitle
        case 'assetLauncherText': return assetLauncherText
        default: return ''
      }
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
    vi.resetModules()
    vi.clearAllMocks()
  })

  it('is a Vue instance', async () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders img, title, text and button as PPR staff', async () => {
    expect(wrapper.find('.product-container').exists()).toBe(true)
    expect(wrapper.find('.product-img').exists()).toBe(true)
    expect(wrapper.find('.product-info').exists()).toBe(true)
    expect(wrapper.find('.product-info h2').text()).toBe('Staff Personal Property Registry')
    expect(wrapper.find('.product-info p').text()).toContain('claims on personal property.')
    expect(wrapper.find('.product-info__btn').exists()).toBe(true)
    expect(wrapper.find('.product-info__btn').text()).toContain('Open')
  })

  it('renders img, title, text and button as MHR staff', async () => {
    userModule.state.currentUser.roles = ['mhr']
    await Vue.nextTick()
    expect(wrapper.find('.product-container').exists()).toBe(true)
    expect(wrapper.find('.product-img').exists()).toBe(true)
    expect(wrapper.find('.product-info').exists()).toBe(true)
    expect(wrapper.find('.product-info h2').text()).toBe('Staff Manufactured Home Registry')
    expect(wrapper.find('.product-info p').text()).toContain('claims on manufactured homes.')
    expect(wrapper.find('.product-info__btn').exists()).toBe(true)
    expect(wrapper.find('.product-info__btn').text()).toContain('Open')
  })

  it('renders img, title, text and button as Asset staff', async () => {
    userModule.state.currentUser.roles = ['mhr', 'ppr']
    await Vue.nextTick()
    expect(wrapper.find('.product-container').exists()).toBe(true)
    expect(wrapper.find('.product-img').exists()).toBe(true)
    expect(wrapper.find('.product-info').exists()).toBe(true)
    expect(wrapper.find('.product-info h2').text()).toBe('Staff Asset Registries')
    expect(wrapper.find('.product-info p').text()).toContain('manufactured homes and register or ' +
        'search for legal claims on personal property.')
    expect(wrapper.find('.product-info__btn').exists()).toBe(true)
    expect(wrapper.find('.product-info__btn').text()).toContain('Open')
  })
})
