
import { createLocalVue, shallowMount } from '@vue/test-utils'
import SelectProductService from '@/components/auth/create-account/SelectProductService.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('SelectProductService.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(VueRouter)
    const userModule = {
      namespaced: true,
      state: {
        currentUser: { 'userName': 'user1' }
      }
    }
    const orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {
        },
        productList: [
          {
            'code': 'PPR',
            'name': 'Personal Property Registry',
            'description': 'test',
            'url': 'https://test.com/ppr',
            'type': 'INTERNAL',
            'mdiIcon': 'mdi-image-outline'
          },
          {
            'code': 'VS',
            'name': 'Wills Registry',
            'description': 'VS',
            'url': 'https://test.com/vs',
            'type': 'PARTNER',
            'mdiIcon': 'mdi-image-outline'
          }
        ],
        currentSelectedProducts: ['VS']
      },
      actions: {
        getProductList: jest.fn(),
        addToCurrentSelectedProducts: jest.fn()
      }
    }

    const store = new Vuex.Store({
      strict: false,
      modules: {
        org: orgModule,
        user: userModule
      }
    })
    const router = new VueRouter()

    wrapperFactory = (propsData) => {
      return shallowMount(SelectProductService, {
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
    expect(wrapper).toBeTruthy()
  })

  it('renders the components properly and address is being shown', () => {
    expect(wrapper.find(SelectProductService).exists()).toBe(true)
  })
})
