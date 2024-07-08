import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import ExtraprovincialRegistrationBc
  from '@/components/auth/staff/continuation-application/ExtraprovincialRegistrationBc.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)

const localVue = createLocalVue()
const vuetify = new Vuetify({})

const continuationReview = {
  filing: {
    continuationIn: {
      business: {
        foundingDate: '2001-05-03T07:00:00.000+00:00',
        identifier: 'A0054444',
        legalName: 'FIRST AWIQ SHOPPING CENTRES BC LIMITED'
      }
    }
  }
}

describe('ExtraprovincialRegistrationBc component', () => {
  let wrapper: Wrapper<ExtraprovincialRegistrationBc>

  beforeAll(async () => {
    wrapper = mount(ExtraprovincialRegistrationBc, {
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
    expect(wrapper.vm.continuationReview).toBeTruthy()
  })

  it('rendered the component', () => {
    expect(wrapper.findComponent(ExtraprovincialRegistrationBc).exists()).toBe(true)
    expect(wrapper.find('#extraprovincial-registration-bc').exists()).toBe(true)
  })

  it('rendered all the sections', () => {
    const sections = wrapper.findAll('section')
    expect(sections.length).toBe(3)
  })

  it('rendered the first section', () => {
    const section = wrapper.findAll('section').at(0)
    expect(section.find('label').text()).toBe('Registration Number in B.C.')
    expect(section.find('#registration-number-bc').text()).toBe('A0054444')
  })

  it('rendered the second section', () => {
    const section = wrapper.findAll('section').at(1)
    expect(section.find('label').text()).toBe('Registered Name in B.C.')
    expect(section.find('#registered-name-bc').text()).toBe('FIRST AWIQ SHOPPING CENTRES BC LIMITED')
  })

  it('rendered the third section', () => {
    const section = wrapper.findAll('section').at(2)
    expect(section.find('label').text()).toBe('Date of Registration in B.C.')
    expect(section.find('#registration-date-bc').text()).toBe('May 3, 2001')
  })
})
