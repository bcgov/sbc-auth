import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import ContinuationAuthorizationReviewResult
  from '@/components/auth/staff/continuation-application/ContinuationAuthorizationReviewResult.vue'
import { ContinuationReviewStatus } from '@/models/continuation-review'
import Vue from 'vue'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)

const localVue = createLocalVue()
const vuetify = new Vuetify({})

const continuationReview = {
  filing: {
    continuationIn: {},
    review: {
      id: 123,
      completingParty: 'Joe Enduser',
      status: ContinuationReviewStatus.AWAITING_REVIEW,
      submissionDate: '2024-07-01T19:00:00.000+00:00',
      creationDate: '2024-07-01T19:00:00.000+00:00'
    }
  }
}

describe('ContinuationAuthorizationReviewResult component', () => {
  let wrapper: Wrapper<ContinuationAuthorizationReviewResult>

  beforeAll(async () => {
    wrapper = mount(ContinuationAuthorizationReviewResult, {
      localVue,
      propsData: { continuationReview },
      vuetify
    })

    // wait for things to stabilize
    await flushPromises()
  })

  afterAll(() => {
    wrapper.destroy()
  })

  it('got the prop', () => {
    expect(wrapper.vm.continuationReview).toEqual(continuationReview)
  })

  it('computed "continuationIn"', () => {
    expect(wrapper.vm.continuationIn).toBeTruthy()
  })

  it.skip('computed "isActionable"', () => {
    expect(wrapper.vm.isActionable).toBe(true)
  })

  it('computed initial "isEmailBodyTextRequired"', () => {
    expect(wrapper.vm.isEmailBodyTextRequired).toBe(false)
  })

  it('computed initial "isEmailBodyTextRequired"', () => {
    expect(wrapper.vm.isEmailBodyTextRequired).toBe(false)
  })

  it('computed initial "emailBodyTextLabel"', () => {
    expect(wrapper.vm.emailBodyTextLabel).toBe('Email Body Text (Optional)')
  })

  it('rendered the component', () => {
    expect(wrapper.findComponent(ContinuationAuthorizationReviewResult).exists()).toBe(true)
    expect(wrapper.find('#continuation-authorization-review-result').exists()).toBe(true)
  })

  it.skip('rendered all the sections', () => {
    const sections = wrapper.findAll('section')
    expect(sections.length).toBe(2)
  })

  it('rendered the first section', () => {
    const section = wrapper.findAll('section').at(0)
    expect(section.find('label').text()).toBe('Previous Correspondence')
    // FUTURE: add more here
  })

  it.skip('rendered the second section', () => {
    const section = wrapper.findAll('section').at(1)
    expect(section.find('label').text()).toBe('Review Result')
    // FUTURE: add more here
  })

  it('rendered a functional select component', () => {
    // BusinessService.downloadDocument = vi.fn().mockResolvedValue(null)

    // const button = wrapper.findAll('section').at(5).find('.download-affidavit-btn')
    // button.trigger('click')
    // expect(BusinessService.downloadDocument).toHaveBeenCalledWith('007bd7bd-d421-49a9-9925-03ce561d044f.pdf',
    //   'My Director Affidavit.pdf')

    // vi.clearAllMocks()
  })

  it('rendered a functional textarea component', () => {
    // BusinessService.downloadDocument = vi.fn().mockResolvedValue(null)

    // const button = wrapper.findAll('section').at(5).find('.download-authorization-btn')
    // button.trigger('click')
    // expect(BusinessService.downloadDocument).toHaveBeenCalledWith('0071dbd6-6095-46f6-b5e4-cc859b0ebf27.pdf',
    //   'My Authorization Document.pdf')

    // vi.clearAllMocks()
  })
})
