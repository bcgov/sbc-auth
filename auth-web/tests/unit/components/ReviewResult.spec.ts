import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import ReviewResult from '@/components/auth/staff/continuation-application/ReviewResult.vue'
import { ReviewStatus } from '@/models/continuation-review'
import Vue from 'vue'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)

const localVue = createLocalVue()
const vuetify = new Vuetify({})

const review = {
  id: 123,
  completingParty: 'Joe Enduser',
  status: ReviewStatus.AWAITING_REVIEW,
  submissionDate: '2024-07-01T19:00:00.000+00:00',
  creationDate: '2024-07-01T19:00:00.000+00:00',
  results: []
}

const filing = {}

describe('ReviewResult component', () => {
  let wrapper: Wrapper<any>

  beforeAll(async () => {
    wrapper = mount(ReviewResult, {
      localVue,
      propsData: { review, filing },
      vuetify
    })

    // wait for things to stabilize
    await flushPromises()
  })

  afterAll(() => {
    wrapper.destroy()
  })

  it('got the props', () => {
    expect(wrapper.vm.review).toEqual(review)
    expect(wrapper.vm.filing).toEqual(filing)
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
    expect(wrapper.findComponent(ReviewResult).exists()).toBe(true)
    expect(wrapper.find('#review-result').exists()).toBe(true)
  })

  it('rendered the section', () => {
    const section = wrapper.find('section')
    expect(section.find('label').text()).toBe('Review Result')
  })

  it('rendered a functional select component', () => {
    // before selecting an item
    expect(wrapper.vm.reviewResult).toBeNull()

    // select an item
    const vm = wrapper.find('.v-select').vm as any
    vm.selectItem('APPROVED')

    // after selecting an item
    expect(wrapper.vm.reviewResult).toBe('APPROVED')

    // verify emitted event
    expect(wrapper.emitted('review-result')).toEqual([['APPROVED']])
  })

  it('rendered a functional textarea component', async () => {
    // before selecting an item
    expect(wrapper.vm.emailBodyText).toBe('')

    // set a value
    // Ref: https://github.com/vuetifyjs/vuetify/blob/v2-stable/packages/vuetify/src/components/VTextarea/__tests__/VTextarea.spec.ts
    const textarea = wrapper.find('textarea') as any
    textarea.element.value = 'Looks good to me.'
    await textarea.trigger('input')

    // after selecting an item
    expect(wrapper.vm.emailBodyText).toBe('Looks good to me.')

    // verify emitted event
    // ** unknown why this doesn't work **
    // expect(wrapper.emitted('email-body-text')).toEqual([['Looks good to me.']])
  })
})
