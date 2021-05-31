import { createLocalVue, mount } from '@vue/test-utils'
import Product from '@/components/auth/common/Product.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)

describe('Product.vue', () => {
  let wrapperFactory: any
  let wrapper: any
  const config = {
    'VUE_APP_ROOT_API': 'https://localhost:8080/api/v1/11',
    'VUE_APP_COPS_REDIRECT_URL': 'https://coops-dev.pathfinder.gov.bc.ca/',
    'VUE_APP_PAY_ROOT_API': 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)

  const productDetails = {
    'code': 'VS',
    'description': 'test',
    'url': 'url',
    'type': 'PARTNER',
    'subscriptionStatus': ''
  }
  const pprProduct = {
    'code': 'PPR',
    'description': 'ppr',
    'url': 'url',
    'type': 'PARTNER',
    'subscriptionStatus': ''
  }
  const isSelected = false
  const props = { productDetails, isSelected }

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const vuetify = new Vuetify({})

    const store = new Vuex.Store({
      state: {},
      strict: false

    })
    wrapperFactory = (propsData) => {
      return mount(Product, {
        localVue,
        store,
        vuetify,
        propsData: {
          ...propsData
        },
        mocks: {
          $t: (mock) => mock,
          $te: (mock) => mock
        }
      })
    }

    wrapper = wrapperFactory(props)

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('Should have h3 with given description', () => {
    wrapper = wrapperFactory(props)
    expect(wrapper.find('h3').text()).toBe(productDetails.description)
  })
  it('Should expand on click', async () => {
    wrapper = wrapperFactory({ productDetails, isSelected: false })

    const readMorebtn = wrapper.find("[data-test='btn-productDetails-VS']")
    expect(wrapper.find("[data-test='div-expanded-product-VS']").exists()).toBeFalsy()

    readMorebtn.trigger('click')
    await wrapper.setProps({ isexpandedView: true })
    await wrapper.vm.$nextTick()
    expect(wrapper.find("[data-test='div-expanded-product-VS']").exists()).toBeTruthy()
  })

  it('Should expand and collaps on isexpandedView change', async () => {
    wrapper = wrapperFactory({ productDetails, isexpandedView: false })

    expect(wrapper.find("[data-test='div-expanded-product-VS']").exists()).toBeFalsy()

    await wrapper.setProps({ isexpandedView: true, isSelected: true })
    await wrapper.vm.$nextTick()
    expect(wrapper.find("[data-test='div-expanded-product-VS']").exists()).toBeTruthy()

    await wrapper.setProps({ isexpandedView: false })
    await wrapper.vm.$nextTick()
    expect(wrapper.find("[data-test='div-expanded-product-VS']").exists()).toBeFalsy()
  })

  it('Should set productSelected on checkbox click', async () => {
    wrapper = wrapperFactory({ productDetails: pprProduct, isexpandedView: false })

    const checkbox = wrapper.find("[data-test='check-product-PPR']")
    checkbox.trigger('change')
    // await wrapper.setProps({ isexpandedView: true })
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.$data.productSelected).toBe(true)
  })
})
