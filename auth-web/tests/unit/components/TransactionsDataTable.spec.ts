import '../test-utils/composition-api-setup' // important to import this first
import { InvoiceStatus, PaymentTypes } from '@/util/constants'
import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import { BaseVDataTable } from '@/components/datatable'
import { DatePicker } from '@/components'
import TransactionsDataTable from '@/components/auth/account-settings/transaction/TransactionsDataTable.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import { axios } from '@/util/http-util'
import { baseVdataTable } from '../test-utils/test-data/baseVdata'
import flushPromises from 'flush-promises'
import { getTransactionTableHeaders } from '@/resources/table-headers'
import sinon from 'sinon'
import { transactionResponse } from '../test-utils'
import { useOrgStore } from '@/stores/org'

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

const heading = '.section-heading'
const header = baseVdataTable.header
const headerTitles = baseVdataTable.headerTitles
const itemRow = baseVdataTable.itemRow
const itemCell = baseVdataTable.itemCell

const config = {
  AUTH_API_URL: 'https://localhost:8080/api/v1/app',
  PAY_API_URL: 'https://pay-api.gov.bc.ca/api/v1'
}

const createTestTransaction = (overrides: any = {}) => ({
  id: 1,
  businessIdentifier: 'TEST123',
  createdOn: '2023-01-01T10:00:00Z',
  createdName: 'Test User',
  folioNumber: 'FOLIO123',
  invoiceNumber: 'INV123',
  lineItems: [{ description: 'Test Service', quantity: 1, price: 100 }],
  details: [],
  paymentAccount: { accountId: '123', accountName: 'Test Account', billable: true },
  paymentMethod: PaymentTypes.PAD,
  product: 'PPR',
  statusCode: InvoiceStatus.PAID,
  total: 100,
  updatedOn: '2023-01-01T10:00:00Z',
  refundDate: null,
  appliedCredits: [],
  partialRefunds: [],
  ...overrides
})

const createAppliedCredit = (overrides: any = {}) => ({
  amountApplied: 100,
  cfsIdentifier: 'CREDIT1',
  createdOn: new Date('2023-01-01T10:00:00Z'),
  creditId: 1,
  invoiceAmount: 100,
  invoiceNumber: 'INV123',
  ...overrides
})

const createPartialRefund = (overrides: any = {}) => ({
  paymentLineItemId: 1,
  refundType: 'PARTIAL',
  refundAmount: 50,
  ...overrides
})

const setupTestWrapper = async (headers = getTransactionTableHeaders()) => {
  const localVue = createLocalVue()
  const orgStore = useOrgStore()
  orgStore.currentOrganization = { id: 123 } as any

  const testSandbox = sinon.createSandbox()
  const get = testSandbox.stub(axios, 'post')
  get.returns(Promise.resolve({ data: transactionResponse }))

  const wrapper = mount(TransactionsDataTable, {
    localVue,
    vuetify,
    propsData: { headers }
  })
  await flushPromises()

  return { wrapper, sandbox: testSandbox }
}

const setupTransactionTest = async (transaction: any, existingWrapper: any) => {
  existingWrapper.setProps({
    transactions: { results: [transaction], totalResults: 1 },
    loading: false
  })
  await Vue.nextTick()

  return { wrapper: existingWrapper }
}

const testDropdownContent = (wrapper: any, transaction: any, expectedLength: number, expectedTypes: any[] = []) => {
  if (expectedLength > 0) {
    const dropdownItems = wrapper.vm.getDropdownItems(transaction)
    expect(dropdownItems).toHaveLength(expectedLength)

    expectedTypes.forEach((expectedType, index) => {
      if (expectedType.type) {
        expect(dropdownItems[index].type).toBe(expectedType.type)
      }
      if (expectedType.paymentMethod) {
        expect(dropdownItems[index].paymentMethod).toBe(expectedType.paymentMethod)
      }
      if (expectedType.amount) {
        expect(dropdownItems[index].amount).toBe(expectedType.amount)
      }
    })
  }
}

const testTransactionScenario = async (transactionOverrides: any, expectedDropdownLength: number, testWrapper: any, expectedTypes: any[] = []) => {
  const transaction = createTestTransaction(transactionOverrides)
  const { wrapper: testWrapperResult } = await setupTransactionTest(transaction, testWrapper)
  testDropdownContent(testWrapperResult, transaction, expectedDropdownLength, expectedTypes)
}

const testRefundScenario = async (transactionOverrides: any, expectedRefundAmount: string, expectedType: string, testWrapper: any) => {
  const transaction = createTestTransaction(transactionOverrides)
  const { wrapper: testWrapperResult } = await setupTransactionTest(transaction, testWrapper)

  const dropdownItems = testWrapperResult.vm.getDropdownItems(transaction)
  const refundItems = dropdownItems.filter(item => item.isRefund)
  expect(refundItems[0].amount).toBe(expectedRefundAmount)
  expect(refundItems[0].type).toBe(expectedType)
}

describe('TransactionsDataTable tests', () => {
  let wrapper: Wrapper<any>
  let sandbox: any

  beforeEach(async () => {
    sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)
    const setup = await setupTestWrapper()
    wrapper = setup.wrapper
    sandbox = setup.sandbox
  }, 50000)

  afterEach(() => {
    if (wrapper) wrapper.destroy()
    if (sandbox) sandbox.restore()
  })

  it('renders transaction table with child components', async () => {
    await wrapper.vm.loadTransactionList()
    expect(wrapper.findComponent(BaseVDataTable).exists()).toBe(true)
    expect(wrapper.findComponent(DatePicker).exists()).toBe(true)
    expect(wrapper.findComponent(DatePicker).isVisible()).toBe(false)
    expect(wrapper.find(heading).exists()).toBe(false)

    expect(wrapper.findComponent(BaseVDataTable).find(header).exists()).toBe(true)
    const titles = wrapper.findComponent(BaseVDataTable).findAll(headerTitles)
    expect(titles.length).toBe(getTransactionTableHeaders().length)
    expect(titles.at(0).text()).toBe('Transaction Type')
    expect(titles.at(1).text()).toBe('Folio #')
    expect(titles.at(2).text()).toBe('Initiated by')
    expect(titles.at(3).text()).toBe('Date (Pacific Time)')
    expect(titles.at(4).text()).toBe('Total Amount')
    expect(titles.at(5).text()).toBe('Transaction ID')
    expect(titles.at(6).text()).toBe('Invoice Reference Number')
    expect(titles.at(7).text()).toBe('Payment Method')
    expect(titles.at(8).text()).toBe('Payment Status')
    expect(titles.at(9).text()).toBe('Downloads')
    expect(titles.at(10).text()).toBe('')

    const itemRows = wrapper.findComponent(BaseVDataTable).findAll(itemRow)
    expect(itemRows.length).toBe(transactionResponse.items.length)

    const row1Cells = itemRows.at(0).findAll(itemCell)
    expect(row1Cells.at(0).find('b').text()).toBe('Statement of Registration')
    expect(row1Cells.at(0).find('span').text()).toBe('label1 value1')
    expect(row1Cells.at(1).text()).toBe('ab12')
    expect(row1Cells.at(2).text()).toBe('tester 123')
    expect(row1Cells.at(3).text()).toContain('January 24, 20236:00 AM')
    expect(row1Cells.at(4).text()).toBe('$0.00')
    expect(row1Cells.at(5).text()).toBe('25663')
    expect(row1Cells.at(6).text()).toBe('REG000123442')
    expect(row1Cells.at(7).text()).toBe('No Fee')
    expect(row1Cells.at(8).text()).toBe('CompletedJanuary 24, 2023')
    expect(row1Cells.at(9).text()).toBe('Receipt')
    expect(row1Cells.at(10).text()).toBe('')

    expect(wrapper.find('.clear-btn').exists()).toBe(false)
  })

  it('shows extended stuff when set', async () => {
    wrapper.setProps({ extended: true, headers: getTransactionTableHeaders(true) })
    await wrapper.vm.loadTransactionList()
    expect(wrapper.find(heading).exists()).toBe(true)
    expect(wrapper.find(heading).text().replaceAll(' ', '').replaceAll('\n', '')).toBe('Transactions')

    expect(wrapper.findComponent(BaseVDataTable).find(header).exists()).toBe(true)
    const titles = wrapper.findComponent(BaseVDataTable).findAll(headerTitles)
    expect(titles.length).toBe(getTransactionTableHeaders(true).length)
    expect(titles.at(0).text()).toBe('Account Name')
    expect(titles.at(1).text()).toBe('Application Type')
    expect(titles.at(2).text()).toBe('Transaction Type')
    expect(titles.at(3).text()).toBe('Transaction Details')
    expect(titles.at(4).text()).toBe('Number')
    expect(titles.at(5).text()).toBe('Folio #')
    expect(titles.at(6).text()).toBe('Initiated by')
    expect(titles.at(7).text()).toBe('Date (Pacific Time)')
    expect(titles.at(8).text()).toBe('Total Amount')
    expect(titles.at(9).text()).toBe('Transaction ID')
    expect(titles.at(10).text()).toBe('Invoice Reference Number')
    expect(titles.at(11).text()).toBe('Payment Method')
    expect(titles.at(12).text()).toBe('Payment Status')
    expect(titles.at(13).text()).toBe('Downloads')
    expect(titles.at(14).text()).toBe('')

    const itemRows = wrapper.findComponent(BaseVDataTable).findAll(itemRow)
    expect(itemRows.length).toBe(transactionResponse.items.length)

    const row1Cells = itemRows.at(0).findAll(itemCell)
    expect(row1Cells.at(0).text()).toBe("Ministry of Citizens' Services-BC Registries and Online Services Staff")
    expect(row1Cells.at(1).text()).toBe('Personal Property Registry')
    expect(row1Cells.at(2).text()).toBe('Statement of Registration')
    expect(row1Cells.at(3).text()).toBe('label1 value1')
    expect(row1Cells.at(4).text()).toBe('123')
    expect(row1Cells.at(5).text()).toBe('ab12')
    expect(row1Cells.at(6).text()).toBe('tester 123')
    expect(row1Cells.at(7).text()).toContain('January 24, 20236:00 AM')
    expect(row1Cells.at(8).text()).toBe('$0.00')
    expect(row1Cells.at(9).text()).toBe('25663')
    expect(row1Cells.at(10).text()).toBe('REG000123442')
    expect(row1Cells.at(11).text()).toBe('No Fee')
    expect(row1Cells.at(12).text()).toBe('CompletedJanuary 24, 2023')
    expect(row1Cells.at(13).text()).toBe('Receipt')
    expect(row1Cells.at(14).text()).toBe('')
  })

  it('shows date picker when date filter clicked', async () => {
    expect(wrapper.findComponent(DatePicker).isVisible()).toBe(false)
    expect(wrapper.find('.date-filter').exists()).toBe(true)
    wrapper.vm.showDatePicker = true
    await Vue.nextTick()
    expect(wrapper.findComponent(DatePicker).isVisible()).toBe(true)
  })

  it('PAID with full applied credit [PAD] - should show Account Credit as payment method and no dropdown', async () => {
    await testTransactionScenario({
      statusCode: InvoiceStatus.PAID,
      paymentMethod: PaymentTypes.PAD,
      total: 100,
      appliedCredits: [createAppliedCredit({ amountApplied: 100 })]
    }, 0, wrapper, [])
  })

  it('PAID with partial applied credit [PAD] - should show combined payment method and dropdown', async () => {
    await testTransactionScenario({
      statusCode: InvoiceStatus.PAID,
      paymentMethod: PaymentTypes.PAD,
      total: 100,
      appliedCredits: [createAppliedCredit({ amountApplied: 60 })]
    }, 2, wrapper, [
      { paymentMethod: 'Account Credit' },
      { paymentMethod: 'PAD' }
    ])
  })

  it('PAID with multiple applied credits [PAD] - should handle multiple applied credits correctly', async () => {
    const transaction = createTestTransaction({
      statusCode: InvoiceStatus.PAID,
      paymentMethod: PaymentTypes.PAD,
      total: 150,
      appliedCredits: [
        createAppliedCredit({
          id: 1,
          amountApplied: 50,
          invoiceAmount: 150
        }),
        createAppliedCredit({
          id: 2,
          amountApplied: 75,
          cfsIdentifier: 'CREDIT2',
          createdOn: new Date('2023-01-02T11:00:00Z'),
          creditId: 2,
          invoiceAmount: 150
        })
      ]
    })

    const { wrapper: testWrapper } = await setupTransactionTest(transaction, wrapper)

    const dropdownItems = testWrapper.vm.getDropdownItems(transaction)
    expect(dropdownItems).toHaveLength(3)

    expect(dropdownItems[0].id).toBe('credit-1')
    expect(dropdownItems[0].amount).toBe('$50.00')
    expect(dropdownItems[0].paymentMethod).toBe('Account Credit')
    expect(dropdownItems[0].transactionId).toBe(1)
    expect(dropdownItems[0].date).toEqual(new Date('2023-01-01T10:00:00Z'))

    expect(dropdownItems[1].id).toBe('credit-2')
    expect(dropdownItems[1].amount).toBe('$75.00')
    expect(dropdownItems[1].paymentMethod).toBe('Account Credit')
    expect(dropdownItems[1].transactionId).toBe(2)
    expect(dropdownItems[1].date).toEqual(new Date('2023-01-02T11:00:00Z'))

    expect(dropdownItems[2].id).toBe('remaining-1')
    expect(dropdownItems[2].amount).toBe('$25.00')
    expect(dropdownItems[2].paymentMethod).toBe('PAD')
    expect(dropdownItems[2].transactionId).toBe(1)
    expect(dropdownItems[2].date).toEqual(new Date('2023-01-01T10:00:00Z'))
  })

  it('CREDITED with refund as credits [PAD] - should show Credited status and dropdown', async () => {
    await testTransactionScenario({
      statusCode: InvoiceStatus.CREDITED,
      paymentMethod: PaymentTypes.PAD,
      total: 100,
      refundDate: '2023-01-02T10:00:00Z'
    }, 1, wrapper, [
      { type: 'Refund as credits', paymentMethod: 'Account Credit' }
    ])
  })

  it('CANCELLED with $0 total [PAD] - should show $0.00 and no dropdown', async () => {
    await testTransactionScenario({
      statusCode: InvoiceStatus.CANCELLED,
      paymentMethod: PaymentTypes.PAD,
      total: 0
    }, 0, wrapper, [])
  })

  it('PAID normal transaction [PAD] - should show normal payment method and no dropdown', async () => {
    await testTransactionScenario({
      statusCode: InvoiceStatus.PAID,
      paymentMethod: PaymentTypes.PAD,
      total: 100
    }, 0, wrapper, [])
  })

  it('PAID with partial refund [DIRECT_PAY] - should show Partially Refunded status and combined refunds', async () => {
    await testRefundScenario({
      statusCode: InvoiceStatus.PAID,
      paymentMethod: PaymentTypes.DIRECT_PAY,
      total: 100,
      partialRefunds: [
        createPartialRefund({ refundAmount: 30, isCredit: false }),
        createPartialRefund({ paymentLineItemId: 2, refundAmount: 20, isCredit: false })
      ]
    }, '-$50.00', 'Refund', wrapper)
  })

  it('PAID with partial credit [PAD] - should show Partially Credited status and Account Credit', async () => {
    const transaction = createTestTransaction({
      statusCode: InvoiceStatus.PAID,
      paymentMethod: PaymentTypes.PAD,
      total: 100,
      partialRefunds: [createPartialRefund({
        isCredit: true,
        createdName: 'Test User',
        createdBy: 'testuser',
        id: 1,
        createdOn: new Date('2023-01-01T10:00:00Z')
      })]
    })

    const { wrapper: testWrapper } = await setupTransactionTest(transaction, wrapper)

    const dropdownItems = testWrapper.vm.getDropdownItems(transaction)
    const refundItem = dropdownItems.find(item => item.isRefund)
    expect(refundItem.paymentMethod).toBe('Account Credit')
    expect(refundItem.status).toBe('Partially Credited')
    expect(refundItem.type).toBe('Refund as credits')
  })

  it('REFUNDED with dropdown rows [DIRECT_PAY] - should show Refunded status and dropdown', async () => {
    await testTransactionScenario({
      statusCode: InvoiceStatus.REFUNDED,
      paymentMethod: PaymentTypes.DIRECT_PAY,
      total: 100,
      refundDate: '2023-01-02T10:00:00Z'
    }, 1, wrapper, [
      { type: 'Refund', paymentMethod: 'DIRECT_PAY' }
    ])
  })

  it('CREDITED with refunds as credits [PAD] - should show Credited status and Account Credit', async () => {
    await testTransactionScenario({
      statusCode: InvoiceStatus.CREDITED,
      paymentMethod: PaymentTypes.PAD,
      total: 100,
      refundDate: '2023-01-02T10:00:00Z'
    }, 1, wrapper, [
      { type: 'Refund as credits', paymentMethod: 'Account Credit' }
    ])
  })
})
