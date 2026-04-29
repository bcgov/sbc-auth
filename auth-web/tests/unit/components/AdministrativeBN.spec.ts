import { Wrapper, mount, shallowMount } from '@vue/test-utils'
import AdministrativeBN from '@/components/auth/staff/admin/AdministrativeBN.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)
const vuetify = new Vuetify({})
// Not mocked globally, because PADInfoForm uses it.
vi.mock('vue-the-mask')

describe('Search Business Form: Initial', () => {
  vi.mock('vue-the-mask')
  const wrapper: Wrapper<any> = mount(AdministrativeBN, {
    vuetify,
    propsData: {}
  })

  afterAll(() => {
    wrapper.destroy()
  })

  it('renders the component properly', () => {
    // verify component
    expect(wrapper.find('#txtBusinessNumber').isVisible()).toBe(true)
    expect(wrapper.find('.search-btn').attributes('disabled')).toBe('disabled')
  })
})

describe('Search Business Form: Result', () => {
  const wrapper: Wrapper<any> = shallowMount(AdministrativeBN, {
    vuetify,
    propsData: {}
  })

  afterAll(() => {
    wrapper.destroy()
  })

  it('renders the component properly', async () => {
    // verify component
    wrapper.setData({ businessDetails: {
      legalName: 'Business Name',
      identifier: 'FM1234567',
      taxId: '123456789BC0001' }
    })
    await flushPromises()
    expect(wrapper.find('.business-details').isVisible()).toBe(true)
  })

  it('shows loading state during preview', async () => {
    wrapper.setData({ businessDetails: {
      legalName: 'Business Name',
      identifier: 'FM1234567',
      taxId: '123456789BC0001' }
    })
    await flushPromises()

    const mockFetch = vi.fn().mockImplementation(() => new Promise(resolve => setTimeout(() => resolve('http://test.com'), 50)))
    wrapper.vm.fetchBusinessSummaryPdfUrl = mockFetch

    const promise = wrapper.vm.previewBusinessSummary()
    expect(wrapper.vm.previewActive).toBe(true)

    await promise
    expect(wrapper.vm.previewActive).toBe(false)
    expect(wrapper.vm.pdfDialog).toBe(true)
    expect(wrapper.vm.pdfUrl).toBe('http://test.com')
  })

  it('shows loading state during download', async () => {
    wrapper.setData({ businessDetails: {
      legalName: 'Business Name',
      identifier: 'FM1234567',
      taxId: '123456789BC0001' }
    })
    await flushPromises()

    const mockDownload = vi.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 50)))
    wrapper.vm.downloadBusinessSummary = mockDownload

    const promise = wrapper.vm.downloadSummary()
    expect(wrapper.vm.downloadActive).toBe(true)

    await promise
    expect(wrapper.vm.downloadActive).toBe(false)
  })

  it('clears business summary pdf data when searching a new business', async () => {
    // mock the window.URL.revokeObjectURL function
    delete window.URL.revokeObjectURL
    window.location = { pathname: vi.fn() } as any
    window.URL.revokeObjectURL = vi.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 50)))

    wrapper.setData({
      businessDetails: {
        legalName: 'Business Name',
        identifier: 'FM1234567',
        taxId: '123456789BC0001'
      },
      pdfDialog: true,
      pdfUrl: 'fake'
    })
    await flushPromises()

    await wrapper.vm.resetSearch()
    expect(wrapper.vm.pdfDialog).toBe(false)
    expect(wrapper.vm.pdfUrl).toBe('')
  })
})
