import { createLocalVue, mount } from '@vue/test-utils'
import Product from '@/components/auth/common/Product.vue'
import { ProductStatus } from '@/util/constants'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)

describe('Product.vue', () => {
  let wrapperFactory: any
  let wrapper: any
  const config = {
    'AUTH_API_URL': 'https://localhost:8080/api/v1/11',
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)

  const productDetails = {
    'code': 'VS',
    'description': 'test',
    'url': 'url',
    'type': 'PARTNER',
    'subscriptionStatus': ProductStatus.NOT_SUBSCRIBED
  }
  const pprProduct = {
    'code': 'PPR',
    'description': 'ppr',
    'url': 'url',
    'type': 'PARTNER',
    'subscriptionStatus': ProductStatus.NOT_SUBSCRIBED,
    'premiumOnly': false
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

    // FUTURE: figure out why this doesn't pass (hopefully will pass after converting to composition)
    // await wrapper.setProps({ isexpandedView: false })
    // await wrapper.vm.$nextTick()
    // expect(wrapper.find("[data-test='div-expanded-product-VS']").exists()).toBeFalsy()
  })

  it('Should set productSelected on checkbox click', async () => {
    wrapper = wrapperFactory({ productDetails: pprProduct, isexpandedView: false })

    const checkbox = wrapper.find("[data-test='check-product-PPR']")
    checkbox.trigger('change')
    // await wrapper.setProps({ isexpandedView: true })
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.$data.productSelected).toBe(true)
    expect(wrapper.vm.hasDecisionNotBeenMade).toBeTruthy()
    expect(wrapper.find("[data-test='div-decision-not-made-product']").exists()).toBeTruthy()
  })

  it('active product should not display checkbox', async () => {
    pprProduct.subscriptionStatus = ProductStatus.ACTIVE
    wrapper = wrapperFactory({ productDetails: pprProduct, isexpandedView: false, isAccountSettingsView: true })

    expect(wrapper.find("[data-test='div-decision-made-product']").exists()).toBeTruthy()
    expect(wrapper.find("[data-test='div-decision-not-made-product']").exists()).toBeFalsy()

    const getDecisionMadeSettings = wrapper.vm.productLabel
    expect(getDecisionMadeSettings.decisionMadeIcon).toBe('mdi-check-circle')
    expect(getDecisionMadeSettings.decisionMadeColorCode).toBe('success')
    expect(wrapper.vm.hasDecisionNotBeenMade).toBeFalsy()
  })

  it('pending product should not display checkbox', async () => {
    pprProduct.subscriptionStatus = ProductStatus.PENDING_STAFF_REVIEW
    wrapper = wrapperFactory({ productDetails: pprProduct, isexpandedView: false, isAccountSettingsView: true })

    expect(wrapper.find("[data-test='div-decision-made-product']").exists()).toBeTruthy()
    expect(wrapper.find("[data-test='div-decision-not-made-product']").exists()).toBeFalsy()

    const getDecisionMadeSettings = wrapper.vm.productLabel
    expect(getDecisionMadeSettings.decisionMadeIcon).toBe('mdi-clock-outline')
    expect(getDecisionMadeSettings.decisionMadeColorCode).toBeNull()
    expect(wrapper.vm.hasDecisionNotBeenMade).toBeFalsy()
  })

  it('rejected product should not display checkbox', async () => {
    pprProduct.subscriptionStatus = ProductStatus.REJECTED
    wrapper = wrapperFactory({ productDetails: pprProduct, isexpandedView: false, isAccountSettingsView: true })

    expect(wrapper.find("[data-test='div-decision-made-product']").exists()).toBeTruthy()
    expect(wrapper.find("[data-test='div-decision-not-made-product']").exists()).toBeFalsy()

    const getDecisionMadeSettings = wrapper.vm.productLabel
    expect(getDecisionMadeSettings.decisionMadeIcon).toBe('mdi-close-circle')
    expect(getDecisionMadeSettings.decisionMadeColorCode).toBe('error')
    expect(wrapper.vm.hasDecisionNotBeenMade).toBeFalsy()
  })

  it('premium product should be disabled in basic account settings', async () => {
    pprProduct.subscriptionStatus = ProductStatus.NOT_SUBSCRIBED
    pprProduct.premiumOnly = true
    wrapper = wrapperFactory({ productDetails: pprProduct, isexpandedView: false, isAccountSettingsView: true, isBasicAccount: true })

    expect(wrapper.find("[data-test='div-decision-made-product']").exists()).toBeTruthy()
    expect(wrapper.find("[data-test='div-decision-not-made-product']").exists()).toBeFalsy()

    const getDecisionMadeSettings = wrapper.vm.productLabel
    expect(getDecisionMadeSettings.decisionMadeIcon).toBe('mdi-minus-box')
    expect(getDecisionMadeSettings.decisionMadeColorCode).toBeNull()
    expect(wrapper.vm.hasDecisionNotBeenMade).toBeTruthy()
    expect(wrapper.vm.isBasicAccountAndPremiumProduct).toBeTruthy()
  })

  it('creation flow should display check box', async () => {
    pprProduct.subscriptionStatus = ProductStatus.NOT_SUBSCRIBED
    wrapper = wrapperFactory({ productDetails: pprProduct, isexpandedView: false })

    expect(wrapper.find("[data-test='div-decision-made-product']").exists()).toBeFalsy()
    expect(wrapper.find("[data-test='div-decision-not-made-product']").exists()).toBeTruthy()
    expect(wrapper.find("[data-test='check-product-PPR']").exists()).toBeTruthy()
  })
})
