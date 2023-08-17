import { createLocalVue, mount } from '@vue/test-utils'

import ProductPackage from '@/components/auth/account-settings/product/ProductPackage.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Account settings ProductPackage.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    const userModule = {
      namespaced: true,
      state: {
        currentUser: {
          fullName: 'user2'
        }
      }

    }
    const orgModule = {
      namespaced: true,
      actions: {
        getOrgProducts: vi.fn(),
        addOrgProducts: vi.fn()
      },
      state: {
        currentOrganization: {
          name: 'test org'
        }
      }
    }

    const store = new Vuex.Store({
      strict: false,
      modules: {
        org: orgModule,
        user: userModule
      }
    })

    wrapperFactory = (propsData) => {
      return mount(ProductPackage, {
        localVue,
        store,
        vuetify,
        propsData: {
          ...propsData
        }
      })
    }

    wrapper = wrapperFactory({})
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the components properly', () => {
    expect(wrapper.findComponent(ProductPackage).exists()).toBe(true)
  })

  it('renders proper header content', () => {
    expect(wrapper.find('h2').text()).toBe('Products and Services')
  })
})
