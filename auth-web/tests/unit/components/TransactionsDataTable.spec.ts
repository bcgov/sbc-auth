import '../test-utils/composition-api-setup' // important to import this first
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

// selectors
const heading = '.section-heading'
const header = baseVdataTable.header
const headerTitles = baseVdataTable.headerTitles
const itemRow = baseVdataTable.itemRow
const itemCell = baseVdataTable.itemCell

describe('TransactionsDataTable tests', () => {
  let wrapper: Wrapper<any>
  let sandbox: any

  const config = {
    AUTH_API_URL: 'https://localhost:8080/api/v1/app',
    PAY_API_URL: 'https://pay-api.gov.bc.ca/api/v1'
  }
  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  const headers = getTransactionTableHeaders()
  const headersExtended = getTransactionTableHeaders(true)

  beforeEach(async () => {
    const localVue = createLocalVue()
    const orgStore = useOrgStore()
    orgStore.currentOrganization = { id: 123 } as any

    // stub get transactions get call
    sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'post')
    get.returns(Promise.resolve({ data: transactionResponse }))

    wrapper = mount(TransactionsDataTable, {
      localVue,
      vuetify,
      propsData: { headers: headers }
    })
    await flushPromises()
  }, 50000)

  afterEach(() => {
    wrapper.destroy()
    sandbox.restore()
  })

  it('renders transaction table with child components', async () => {
    // trigger load
    await wrapper.vm.loadTransactionList()
    expect(wrapper.findComponent(BaseVDataTable).exists()).toBe(true)
    expect(wrapper.findComponent(DatePicker).exists()).toBe(true)
    expect(wrapper.findComponent(DatePicker).isVisible()).toBe(false)
    expect(wrapper.find(heading).exists()).toBe(false)
    // table headers
    expect(wrapper.findComponent(BaseVDataTable).find(header).exists()).toBe(true)
    const titles = wrapper.findComponent(BaseVDataTable).findAll(headerTitles)
    expect(titles.length).toBe(headers.length)
    expect(titles.at(0).text()).toBe('Transaction Type')
    expect(titles.at(1).text()).toBe('Folio #')
    expect(titles.at(2).text()).toBe('Initiated by')
    expect(titles.at(3).text()).toBe('Date (Pacific Time)')
    expect(titles.at(4).text()).toBe('Total Amount')
    expect(titles.at(5).text()).toBe('Transaction ID')
    expect(titles.at(6).text()).toBe('Invoice Reference Number')
    expect(titles.at(7).text()).toBe('Payment Method')
    expect(titles.at(8).text()).toBe('Payment Status')
    expect(titles.at(9).text()).toBe('')
    // table items
    const itemRows = wrapper.findComponent(BaseVDataTable).findAll(itemRow)
    expect(itemRows.length).toBe(transactionResponse.items.length)
    // test cell data
    const row1Cells = itemRows.at(0).findAll(itemCell)
    expect(row1Cells.at(0).find('b').text()).toBe('Statement of Registration')
    expect(row1Cells.at(0).find('span').text()).toBe('label1 value1')
    expect(row1Cells.at(1).text()).toBe('ab12')
    expect(row1Cells.at(2).text()).toBe('tester 123')
    // Input:createdOn: '2023-01-24T14:00:00'
    expect(row1Cells.at(3).text()).toContain('January 24, 20236:00 AM')
    expect(row1Cells.at(4).text()).toBe('$0.00')
    expect(row1Cells.at(5).text()).toBe('25663')
    expect(row1Cells.at(6).text()).toBe('REG000123442')
    expect(row1Cells.at(7).text()).toBe('No Fee')
    expect(row1Cells.at(8).text()).toBe('CompletedJanuary 24, 2023')
    expect(row1Cells.at(9).text()).toBe('')
    // clear filters is hidden
    expect(wrapper.find('.clear-btn').exists()).toBe(false)
  })

  it('shows extended stuff when set', async () => {
    wrapper.setProps({ extended: true, headers: headersExtended })
    // trigger load
    await wrapper.vm.loadTransactionList()
    expect(wrapper.find(heading).exists()).toBe(true)
    expect(wrapper.find(heading).text().replaceAll(' ', '').replaceAll('\n', '')).toBe('Transactions(2)')
    // table headers
    expect(wrapper.findComponent(BaseVDataTable).find(header).exists()).toBe(true)
    const titles = wrapper.findComponent(BaseVDataTable).findAll(headerTitles)
    expect(titles.length).toBe(headersExtended.length)
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
    expect(titles.at(13).text()).toBe('')
    // table items
    const itemRows = wrapper.findComponent(BaseVDataTable).findAll(itemRow)
    expect(itemRows.length).toBe(transactionResponse.items.length)
    // test cell data
    const row1Cells = itemRows.at(0).findAll(itemCell)
    expect(row1Cells.at(0).text()).toBe("Ministry of Citizens' Services-BC Registries and Online Services Staff")
    expect(row1Cells.at(1).text()).toBe('Personal Property Registry')
    expect(row1Cells.at(2).text()).toBe('Statement of Registration')
    expect(row1Cells.at(3).text()).toBe('label1 value1')
    expect(row1Cells.at(4).text()).toBe('123')
    expect(row1Cells.at(5).text()).toBe('ab12')
    expect(row1Cells.at(6).text()).toBe('tester 123')
    // Input:createdOn: 2023-01-24T14:00:00
    expect(row1Cells.at(7).text()).toContain('January 24, 20236:00 AM')
    expect(row1Cells.at(8).text()).toBe('$0.00')
    expect(row1Cells.at(9).text()).toBe('25663')
    expect(row1Cells.at(10).text()).toBe('REG000123442')
    expect(row1Cells.at(11).text()).toBe('No Fee')
    expect(row1Cells.at(12).text()).toBe('CompletedJanuary 24, 2023')
    expect(row1Cells.at(13).text()).toBe('')
  })

  it('shows date picker when date filter clicked', async () => {
    // verify setup
    expect(wrapper.findComponent(DatePicker).isVisible()).toBe(false)
    expect(wrapper.find('.date-filter').exists()).toBe(true)
    // simulate click (trigger click not working in this test)
    wrapper.vm.showDatePicker = true
    await Vue.nextTick()
    expect(wrapper.findComponent(DatePicker).isVisible()).toBe(true)
  })
})
