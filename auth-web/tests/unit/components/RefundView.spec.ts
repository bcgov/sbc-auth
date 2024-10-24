import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import RefundViewVue from '@/views/pay/RefundView.vue'
import { VueConstructor } from 'vue'
import Vuetify from 'vuetify'
import { axios } from '@/util/http-util'
import { setupIntersectionObserverMock } from '../util/helper-functions'
import sinon from 'sinon'

sessionStorage.setItem('AUTH_API_CONFIG', JSON.stringify({
  AUTH_API_URL: 'https://localhost:8080/api/v1/11',
  PAY_API_URL: 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
}))

const vuetify = new Vuetify({})
const invoiceInputSelector = '#invoice-id-input'
const fetchInvoiceBtnSelector = '#fetch-invoice-btn'
const partialRefundBtnActionSelector = '#partial-refund-action-btn'
const refundTypeRadioGroupSelector = '#refund-type-radio-group'
const partialRefundRadioSelector = '#radio-partial-refund'
const partialRefundCcWarningSelector = '#partial-refund-cc-warning'
const partialRefundInfoSelector = '#partial-refund-add-refund-info'
const invoiceLineItemsTableSelector = '#invoice-line-items-table'
const invoiceLineItemsHeadersSelector = '#invoice-line-items-headers'
const partialRefundSummaryInfoSelector = '#partial-refund-summary-info'
const refundSummaryTableSelector = '#refund-summary-table'
const refundSummaryHeadersSelector = '#refund-summary-headers'

const headers = [
  'Line Item #',
  'Description',
  'Filing Fee',
  'Priority Fee',
  'Future Effective Fees',
  'Service Fees',
  'Action'
]

describe('RefundView.vue', () => {
  setupIntersectionObserverMock()
  let wrapper: Wrapper<any>
  let localVue: VueConstructor<any>
  let invoiceResponse: any
  let sandbox: sinon.SinonSandbox

  beforeEach(async () => {
    localVue = createLocalVue()
    invoiceResponse = {
      'id': 3828,
      'lineItems': [
        {
          'id': 5335,
          'description': 'Item 1',
          'filingFees': 20.0,
          'futureEffectiveFees': 0.0,
          'priorityFees': 33.0,
          'serviceFees': 1.5,
          'total': 53.0
        },
        {
          'id': 5336,
          'description': 'Item 2',
          'filingFees': 10.0,
          'futureEffectiveFees': 5.0,
          'priorityFees': 0.0,
          'serviceFees': 1.5,
          'total': 10.0
        }
      ],
      'paid': 66.0,
      'paymentMethod': 'DIRECT_PAY'
    }

    sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'get')
    get.returns(Promise.resolve({ data: invoiceResponse }))

    wrapper = mount(RefundViewVue, {
      localVue,
      vuetify
    })
    await wrapper.vm.$nextTick()
  })

  afterEach(() => {
    wrapper.destroy()
    sessionStorage.clear()
    sandbox.restore()

    vi.resetModules()
    vi.clearAllMocks()
  })

  function getTextFieldValue (element) {
    return element.findComponent({ name: 'v-text-field' }).props('value')
  }

  it('Renders Full/Partial Refund Views', async () => {
    expect(wrapper.find(invoiceLineItemsTableSelector).exists()).toBe(true)
    expect(wrapper.find(invoiceInputSelector).exists()).toBe(true)
    expect(wrapper.find(fetchInvoiceBtnSelector).exists()).toBe(true)
    expect(wrapper.find(refundTypeRadioGroupSelector).exists()).toBe(true)

    expect(wrapper.find(refundSummaryTableSelector).exists()).toBe(false)
    expect(wrapper.find(partialRefundCcWarningSelector).exists()).toBe(false)
    expect(wrapper.find(partialRefundInfoSelector).exists()).toBe(false)
    expect(wrapper.find(partialRefundSummaryInfoSelector).exists()).toBe(false)

    const refundPartialRadio = wrapper.find(partialRefundRadioSelector)
    expect(refundPartialRadio.exists()).toBe(true)
    await refundPartialRadio.setChecked()
    expect(wrapper.vm.refundType).toBe(wrapper.vm.RefundType.PARTIAL)

    await wrapper.vm.$nextTick()
    expect(wrapper.find(refundSummaryTableSelector).exists()).toBe(true)
    expect(wrapper.find(partialRefundInfoSelector).exists()).toBe(true)
    expect(wrapper.find(partialRefundSummaryInfoSelector).exists()).toBe(true)

    const invoiceInput = wrapper.find(invoiceInputSelector)
    const fetchInvoiceBtn = wrapper.find(fetchInvoiceBtnSelector)

    await invoiceInput.setValue('1234')
    expect(wrapper.vm.invoiceId).toBe('1234')
    await fetchInvoiceBtn.trigger('click')
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.paymentLineItems.length).toBe(2)

    // Confirm Invoice Line item table renders properly
    expect(wrapper.find(invoiceLineItemsHeadersSelector).exists()).toBe(true)
    const titles = wrapper.find(invoiceLineItemsHeadersSelector)
      .findAll('[id^="header-items-"]')
    expect(titles.length).toBe(headers.length)
    for (let i = 0; i < headers.length; i++) {
      expect(titles.at(i).text()).toBe(headers[i])
    }
    const itemRows = wrapper.find(invoiceLineItemsTableSelector).findAll('[id="item-row"]')
    expect(itemRows.length).toBe(invoiceResponse.lineItems.length)
    const lineItems = invoiceResponse.lineItems
    for (let i = 0; i < lineItems.length; i++) {
      const columns = itemRows.at(i).findAll('td')
      expect(columns.at(0).text()).toBe((i + 1).toString())
      expect(columns.at(1).text()).toBe(lineItems[i].description)
      expect(getTextFieldValue(columns.at(2))).toBe(lineItems[i].filingFees)
      expect(getTextFieldValue(columns.at(3))).toBe(lineItems[i].priorityFees)
      expect(getTextFieldValue(columns.at(4))).toBe(lineItems[i].futureEffectiveFees)
      expect(getTextFieldValue(columns.at(5))).toBe(lineItems[i].serviceFees)
      const actionButton = columns.at(6).find(partialRefundBtnActionSelector)
      expect(actionButton.exists()).toBe(true)

      // Add refund to summary table
      await actionButton.trigger('click')
    }
    await wrapper.vm.$nextTick()

    // Confirm summary table renders properly
    expect(wrapper.find(refundSummaryTableSelector).exists()).toBe(true)
    const summaryTitles = wrapper.find(refundSummaryHeadersSelector)
      .findAll('[id^="header-summary-items-"]')
    expect(summaryTitles.length).toBe(headers.length - 1)
    for (let i = 0; i < headers.length - 1; i++) {
      expect(summaryTitles.at(i).text()).toBe(headers[i])
    }
    const refundItems = wrapper.vm.refundItems
    const paymentLineItems = wrapper.vm.paymentLineItems
    expect(refundItems.length === paymentLineItems.length).toBe(true)
    for (let i = 0; i < refundItems.length; i++) {
      const columns = itemRows.at(i).findAll('td')
      const refundItemIndex = refundItems[i]
      expect(columns.at(0).text()).toBe((refundItemIndex + 1).toString())
      expect(columns.at(1).text()).toBe(paymentLineItems[refundItemIndex].description)
      expect(getTextFieldValue(columns.at(2))).toBe(paymentLineItems[refundItemIndex].filingFees)
      expect(getTextFieldValue(columns.at(3))).toBe(paymentLineItems[refundItemIndex].priorityFees)
      expect(getTextFieldValue(columns.at(4))).toBe(paymentLineItems[refundItemIndex].futureEffectiveFees)
      expect(getTextFieldValue(columns.at(5))).toBe(paymentLineItems[refundItemIndex].serviceFees)
    }
  })

  it('Test full refund payload generation', async () => {
    const invoiceInput = wrapper.find(invoiceInputSelector)
    const fetchInvoiceBtn = wrapper.find(fetchInvoiceBtnSelector)

    await invoiceInput.setValue('1234')
    expect(wrapper.vm.invoiceId).toBe('1234')
    await fetchInvoiceBtn.trigger('click')
    await wrapper.vm.$nextTick()

    wrapper.vm.refundComment = 'refund comment'
    const refundPayload = wrapper.vm.getRefundPayload()
    expect(refundPayload.reason === 'refund comment')
    expect(refundPayload.refundRevenue.length).toBe(0)
  })

  it('Test partial refund payload generation', async () => {
    const refundPartialRadio = wrapper.find(partialRefundRadioSelector)
    expect(refundPartialRadio.exists()).toBe(true)
    await refundPartialRadio.setChecked()

    const invoiceInput = wrapper.find(invoiceInputSelector)
    const fetchInvoiceBtn = wrapper.find(fetchInvoiceBtnSelector)

    await invoiceInput.setValue('1234')
    expect(wrapper.vm.invoiceId).toBe('1234')
    await fetchInvoiceBtn.trigger('click')
    await wrapper.vm.$nextTick()

    wrapper.vm.refundItems = [0, 1]
    wrapper.vm.refundComment = 'refund comment'
    await wrapper.vm.$nextTick()

    let refundPayload = wrapper.vm.getRefundPayload()
    expect(refundPayload.reason === 'refund comment')
    expect(refundPayload.refundRevenue.length).toBe(6)

    // Test all line items without adjusting refund amounts
    const RefundLineTypes = wrapper.vm.RefundLineTypes
    const paymentLineItems = wrapper.vm.paymentLineItems
    let firstLineItemRefunds = refundPayload.refundRevenue
      .filter(item => item.paymentLineItemId === paymentLineItems[0].id)
    let secondLineItemRefunds = refundPayload.refundRevenue
      .filter(item => item.paymentLineItemId === wrapper.vm.paymentLineItems[1].id)
    expect(firstLineItemRefunds.length).toBe(3)
    expect(firstLineItemRefunds[0].refundType === RefundLineTypes.BASE_FEES)
    expect(firstLineItemRefunds[0].refundAmount === paymentLineItems[0].filingFees)
    expect(firstLineItemRefunds[1].refundType === RefundLineTypes.PRIORITY_FEES)
    expect(firstLineItemRefunds[1].refundAmount === paymentLineItems[0].priorityFees)
    expect(firstLineItemRefunds[2].refundType === RefundLineTypes.SERVICE_FEES)
    expect(firstLineItemRefunds[2].refundAmount === paymentLineItems[0].serviceFees)
    expect(secondLineItemRefunds.length).toBe(3)
    expect(secondLineItemRefunds[0].refundType === RefundLineTypes.BASE_FEES)
    expect(secondLineItemRefunds[0].refundAmount === paymentLineItems[1].filingFees)
    expect(secondLineItemRefunds[1].refundType === RefundLineTypes.FUTURE_EFFECTIVE_FEES)
    expect(secondLineItemRefunds[1].refundAmount === paymentLineItems[1].futureEffectiveFees)
    expect(secondLineItemRefunds[2].refundType === RefundLineTypes.SERVICE_FEES)
    expect(secondLineItemRefunds[2].refundAmount === paymentLineItems[1].serviceFees)

    // Test partial refunds with adjustments
    paymentLineItems[0].filingFees = 15
    paymentLineItems[0].priorityFees = 0
    paymentLineItems[0].serviceFees = 0
    paymentLineItems[1].filingFees = 0
    paymentLineItems[1].futureEffectiveFees = 2.5
    paymentLineItems[1].serviceFees = 1.5

    refundPayload = wrapper.vm.getRefundPayload()
    firstLineItemRefunds = refundPayload.refundRevenue
      .filter(item => item.paymentLineItemId === paymentLineItems[0].id)
    secondLineItemRefunds = refundPayload.refundRevenue
      .filter(item => item.paymentLineItemId === wrapper.vm.paymentLineItems[1].id)
    expect(firstLineItemRefunds.length).toBe(1)
    expect(firstLineItemRefunds[0].refundType === RefundLineTypes.BASE_FEES)
    expect(firstLineItemRefunds[0].refundAmount === 15)
    expect(secondLineItemRefunds.length).toBe(2)
    expect(secondLineItemRefunds[0].refundType === RefundLineTypes.FUTURE_EFFECTIVE_FEES)
    expect(secondLineItemRefunds[0].refundAmount === 2.5)
    expect(secondLineItemRefunds[1].refundType === RefundLineTypes.SERVICE_FEES)
    expect(secondLineItemRefunds[1].refundAmount === 1.5)
  })
})
