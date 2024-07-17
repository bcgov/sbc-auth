import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import BusinessService from '@/services/business.services'
import ContinuationAuthorizationReview from '@/views/auth/staff/ContinuationAuthorizationReview.vue'
import ExtraprovincialRegistrationBc
  from '@/components/auth/staff/continuation-application/ExtraprovincialRegistrationBc.vue'
import HomeJurisdictionInformation
  from '@/components/auth/staff/continuation-application/HomeJurisdictionInformation.vue'
import PreviousCorrespondence from '@/components/auth/staff/continuation-application/PreviousCorrespondence.vue'
import ReviewResult from '@/components/auth/staff/continuation-application/ReviewResult.vue'
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
        filingLink: 'https://filingLink'
      })
    })

    // mock "fetchFiling" business service
    vi.spyOn(BusinessService, 'fetchFiling').mockImplementation((): any => {
      return Promise.resolve({
        header: {},
        business: {},
        continuationIn: {
          mode: 'EXPRO'
        }
      })
    })

    wrapper = mount(ContinuationAuthorizationReview, {
      localVue,
      propsData: { reviewId: 123 },
      stubs: {
        ExtraprovincialRegistrationBc: true,
        HomeJurisdictionInformation: true,
        PreviousCorrespondence: true,
        ReviewResult: true
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
    expect(wrapper.vm.review).toBeTruthy()
  })

  it('fetched the continuation filing object', () => {
    expect(wrapper.vm.filing).toBeTruthy()
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

  it('rendered the third v-card', () => {
    expect(wrapper.find('h2').text()).toBe('Continuation Authorization Review Result')
    const vcard2 = wrapper.find('#continuation-authorization-review-result-vcard')
    expect(vcard2.exists()).toBe(true)
    expect(vcard2.findComponent(PreviousCorrespondence).exists()).toBe(true)
    expect(vcard2.findComponent(ReviewResult).exists()).toBe(true)
  })
})
