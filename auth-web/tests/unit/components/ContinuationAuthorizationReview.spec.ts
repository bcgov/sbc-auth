import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import BusinessService from '@/services/business.services'
import ContinuationAuthorizationReview from '@/views/auth/staff/ContinuationAuthorizationReview.vue'
import ExtraprovincialRegistrationBc from '@/components/auth/staff/continuation-application/ExtraprovincialRegistrationBc.vue'
import HomeJurisdictionInformation from '@/components/auth/staff/continuation-application/HomeJurisdictionInformation.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)

const localVue = createLocalVue()
const vuetify = new Vuetify({})

describe('ExtraprovincialRegistrationBc component', () => {
  let wrapper: Wrapper<ContinuationAuthorizationReview>

  beforeAll(async () => {
    // mock "fetchContinuationReview" business service
    vi.spyOn(BusinessService, 'fetchContinuationReview').mockImplementation((): any => {
      return Promise.resolve({
        review: {},
        results: {},
        filing: {
          continuationIn: {
            mode: 'EXPRO'
          }
        }
      })
    })

    wrapper = mount(ContinuationAuthorizationReview, {
      localVue,
      propsData: { reviewId: 123 },
      stubs: {
        ExtraprovincialRegistrationBc: true,
        HomeJurisdictionInformation: true
      },
      vuetify
    })

    // wait for things to stabilize
    await flushPromises()
  })

  afterAll(() => {
    wrapper.destroy()
  })

  it('got the prop', () => {
    expect(wrapper.vm.reviewId).toBe(123)
  })

  it('fetched the continuation review object', () => {
    expect(wrapper.vm.continuationReview).toBeTruthy()
  })

  it('computed "isExpro"', () => {
    expect(wrapper.vm.isExpro).toBe(true)
  })

  it('rendered the component', () => {
    expect(wrapper.findComponent(ContinuationAuthorizationReview).exists()).toBe(true)
    expect(wrapper.find('#continuation-authorization-review').exists()).toBe(true)
  })

  it('rendered the error dialog', () => {
    expect(wrapper.find('.notify-dialog').exists()).toBe(true)
  })

  it('rendered the container header', () => {
    expect(wrapper.find('.view-header').exists()).toBe(true)
    expect(wrapper.find('h1').text()).toBe('Continuation Authorization Review')
  })

  it('rendered the first v-card', () => {
    const vcard1 = wrapper.find('#extraprovincial-registration-bc-vcard')
    expect(vcard1.exists()).toBe(true)
    expect(vcard1.find('header').text()).toBe('Extraprovincial Registration in B.C.')
    expect(vcard1.findComponent(ExtraprovincialRegistrationBc).exists()).toBe(true)
  })

  it('rendered the second v-card', () => {
    const vcard2 = wrapper.find('#home-jurisdiction-information-vcard')
    expect(vcard2.exists()).toBe(true)
    expect(vcard2.find('header').text()).toBe('Home Jurisdiction Information')
    expect(vcard2.findComponent(HomeJurisdictionInformation).exists()).toBe(true)
  })
})
