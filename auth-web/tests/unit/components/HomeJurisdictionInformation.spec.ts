import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import BusinessService from '@/services/business.services'
import HomeJurisdictionInformation from '@/components/auth/staff/continuation-in/HomeJurisdictionInformation.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)

const localVue = createLocalVue()
const vuetify = new Vuetify({})

const continuationReview = {
  filing: {
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
}

describe('HomeJurisdictionInformation component', () => {
  let wrapper: Wrapper<HomeJurisdictionInformation>

  beforeAll(async () => {
    wrapper = mount(HomeJurisdictionInformation, {
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

  it('rendered all the articles', () => {
    const articles = wrapper.findAll('article')
    expect(articles.length).toBe(7)
  })

  it('rendered the first article', () => {
    const article = wrapper.findAll('article').at(0)
    expect(article.find('label').text()).toBe('Home Jurisdiction')
    expect(article.find('#home-jurisdiction').text()).toBe('Alberta')
  })

  it('rendered the second article', () => {
    const article = wrapper.findAll('article').at(1)
    expect(article.find('label').text()).toBe('Identifying Number in Home Jurisdiction')
    expect(article.find('#identifying-number-home').text()).toBe('AB-5444')
  })

  it('rendered the third article', () => {
    const article = wrapper.findAll('article').at(2)
    expect(article.find('label').text()).toBe('Registered Name in Home Jurisdiction')
    expect(article.find('#registered-name-home').text()).toBe('FIRST AWIQ SHOPPING CENTRES ALBERTA UNLIMITED')
  })

  it('rendered the fourth article', () => {
    const article = wrapper.findAll('article').at(3)
    expect(article.find('label').text()).toBe('Business Number')
    expect(article.find('#business-number').text()).toBe('123456789')
  })

  it('rendered the fifth article', () => {
    const article = wrapper.findAll('article').at(4)
    expect(article.find('label').text())
      .toBe('Date of Incorporation, Continuation, or Amalgamation in Foreign Jurisdiction')
    expect(article.find('#incorporation-date-home').text()).toBe('April 2, 2001')
  })

  it('rendered the sixth article', () => {
    const article = wrapper.findAll('article').at(5)
    expect(article.find('label').text()).toBe('Continuation Authorization')
  })

  it('rendered the seventh article', () => {
    const article = wrapper.findAll('article').at(6)
    expect(article.find('label').text()).toBe('Authorization Date')
    expect(article.find('#authorization-date').text()).toBe('July 1, 2024')
  })

  it('rendered a functional affidavit download button', () => {
    BusinessService.downloadDocument = vi.fn().mockResolvedValue(null)

    const button = wrapper.findAll('article').at(5).find('.download-affidavit-btn')
    button.trigger('click')
    expect(BusinessService.downloadDocument).toHaveBeenCalledWith('007bd7bd-d421-49a9-9925-03ce561d044f.pdf',
      'My Director Affidavit.pdf')

    vi.clearAllMocks()
  })

  it('rendered a functional authorization download button', () => {
    BusinessService.downloadDocument = vi.fn().mockResolvedValue(null)

    const button = wrapper.findAll('article').at(5).find('.download-authorization-btn')
    button.trigger('click')
    expect(BusinessService.downloadDocument).toHaveBeenCalledWith('0071dbd6-6095-46f6-b5e4-cc859b0ebf27.pdf',
      'My Authorization Document.pdf')

    vi.clearAllMocks()
  })
})
