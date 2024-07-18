import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import BusinessService from '@/services/business.services'
import HomeJurisdictionInformation
  from '@/components/auth/staff/continuation-application/HomeJurisdictionInformation.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)

const localVue = createLocalVue()
const vuetify = new Vuetify({})

const review = {}

const filing = {
  continuationIn: {
    authorization: {
      date: '2024-07-01',
      files: [
        {
          fileKey: '0071dbd6-6095-46f6-b5e4-cc859b0ebf27.pdf',
          fileName: 'My Authorization Document.pdf'
        }
      ]
    },
    foreignJurisdiction: {
      affidavitFileKey: '007bd7bd-d421-49a9-9925-03ce561d044f.pdf',
      affidavitFileName: 'My Director Affidavit.pdf',
      country: 'CA',
      identifier: 'AB-5444',
      incorporationDate: '2001-04-02',
      legalName: 'FIRST AWIQ SHOPPING CENTRES ALBERTA UNLIMITED',
      region: 'AB',
      taxId: '123456789'
    },
    nameRequest: {
      legalType: 'CUL'
    }
  }
}

describe('HomeJurisdictionInformation component', () => {
  let wrapper: Wrapper<any>

  beforeAll(async () => {
    wrapper = mount(HomeJurisdictionInformation, {
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

  it('computed "isContinuationInAffidavitRequired"', () => {
    expect(wrapper.vm.isContinuationInAffidavitRequired).toBe(true)
  })

  it('rendered the component', () => {
    expect(wrapper.findComponent(HomeJurisdictionInformation).exists()).toBe(true)
    expect(wrapper.find('#home-jurisdiction-information').exists()).toBe(true)
  })

  it('rendered the error dialog', () => {
    expect(wrapper.find('.notify-dialog').exists()).toBe(true)
  })

  it('rendered all the sections', () => {
    const sections = wrapper.findAll('section')
    expect(sections.length).toBe(7)
  })

  it('rendered the first section', () => {
    const section = wrapper.findAll('section').at(0)
    expect(section.find('label').text()).toBe('Home Jurisdiction')
    expect(section.find('#home-jurisdiction').text()).toBe('Alberta')
  })

  it('rendered the second section', () => {
    const section = wrapper.findAll('section').at(1)
    expect(section.find('label').text()).toBe('Identifying Number in Home Jurisdiction')
    expect(section.find('#identifying-number-home').text()).toBe('AB-5444')
  })

  it('rendered the third section', () => {
    const section = wrapper.findAll('section').at(2)
    expect(section.find('label').text()).toBe('Registered Name in Home Jurisdiction')
    expect(section.find('#registered-name-home').text()).toBe('FIRST AWIQ SHOPPING CENTRES ALBERTA UNLIMITED')
  })

  it('rendered the fourth section', () => {
    const section = wrapper.findAll('section').at(3)
    expect(section.find('label').text()).toBe('Business Number')
    expect(section.find('#business-number').text()).toBe('123456789')
  })

  it('rendered the fifth section', () => {
    const section = wrapper.findAll('section').at(4)
    expect(section.find('label').text())
      .toBe('Date of Incorporation, Continuation, or Amalgamation in Foreign Jurisdiction')
    expect(section.find('#incorporation-date-home').text()).toBe('April 2, 2001')
  })

  it('rendered the sixth section', () => {
    const section = wrapper.findAll('section').at(5)
    expect(section.find('label').text()).toBe('Continuation Authorization')
  })

  it('rendered the seventh section', () => {
    const section = wrapper.findAll('section').at(6)
    expect(section.find('label').text()).toBe('Authorization Date')
    expect(section.find('#authorization-date').text()).toBe('July 1, 2024')
  })

  it('rendered a functional affidavit download button', () => {
    BusinessService.downloadDocument = vi.fn().mockResolvedValue(null)

    const button = wrapper.findAll('section').at(5).find('.download-affidavit-btn')
    button.trigger('click')
    expect(BusinessService.downloadDocument).toHaveBeenCalledWith('007bd7bd-d421-49a9-9925-03ce561d044f.pdf',
      'My Director Affidavit.pdf')

    vi.clearAllMocks()
  })

  it('rendered a functional authorization download button', () => {
    BusinessService.downloadDocument = vi.fn().mockResolvedValue(null)

    const button = wrapper.findAll('section').at(5).find('.download-authorization-btn')
    button.trigger('click')
    expect(BusinessService.downloadDocument).toHaveBeenCalledWith('0071dbd6-6095-46f6-b5e4-cc859b0ebf27.pdf',
      'My Authorization Document.pdf')

    vi.clearAllMocks()
  })
})
