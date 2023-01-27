import '../util/composition-api-setup' // important to import this first
import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import { BaseVDataTable } from '@/components/datatable'
import { DatePicker } from '@/components'
import { TransactionTableHeaders } from '@/resources/table-headers'
import TransactionsDataTable from '@/components/auth/account-settings/transaction/TransactionsDataTable.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import { axios } from '@/util/http-util'
import flushPromises from 'flush-promises'
import sinon from 'sinon'
import { transactionResponse } from '../test-utils'

Vue.use(Vuetify)
Vue.use(Vuex)

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

// selectors
const header = '.base-table__header'
const headerTitles = `${header}__title`
const itemRow = '.base-table__item-row'
const itemCell = '.base-table__item-cell'

describe('TransactionsDataTable tests', () => {
  let wrapper: Wrapper<any>
  let sandbox: any

  const config = {
    AUTH_API_URL: 'https://localhost:8080/api/v1/app',
    PAY_API_URL: 'https://pay-api.gov.bc.ca/api/v1'
  }
  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeAll(async () => {
    const localVue = createLocalVue()
    // store
    const orgModule = { namespaced: true, state: { currentOrganization: { id: 123 } } }
    const store = new Vuex.Store({ strict: false, modules: { org: orgModule } })

    // stub get transactions get call
    sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'post')
    get.returns(new Promise(resolve => resolve({ data: transactionResponse })))

    wrapper = mount(TransactionsDataTable, {
      localVue,
      vuetify,
      store,
      propsData: { headers: TransactionTableHeaders }
    })
    await flushPromises()
  }, 50000)

  afterAll(() => {
    wrapper.destroy()
    sandbox.restore()
  })

  it('renders transaction table with child components', async () => {
    // trigger load
    await wrapper.vm.loadTransactionList()
    expect(wrapper.find(BaseVDataTable).exists()).toBe(true)
    expect(wrapper.find(DatePicker).exists()).toBe(true)
    expect(wrapper.find(DatePicker).isVisible()).toBe(false)
    // table headers
    expect(wrapper.find(BaseVDataTable).find(header).exists()).toBe(true)
    const titles = wrapper.find(BaseVDataTable).findAll(headerTitles)
    expect(titles.length).toBe(TransactionTableHeaders.length)
    expect(titles.at(0).text()).toBe('Transaction Type')
    expect(titles.at(1).text()).toBe('Folio #')
    expect(titles.at(2).text()).toBe('Initiated by')
    expect(titles.at(3).text()).toBe('Date (Pacific Time)')
    expect(titles.at(4).text()).toBe('Total Amount')
    expect(titles.at(5).text()).toBe('Transaction ID')
    expect(titles.at(6).text()).toBe('Payment Method')
    expect(titles.at(7).text()).toBe('Payment Status')
    expect(titles.at(8).text()).toBe('')
    // table items
    const itemRows = wrapper.find(BaseVDataTable).findAll(itemRow)
    expect(itemRows.length).toBe(transactionResponse.items.length)
    // test cell data
    const row1Cells = itemRows.at(0).findAll(itemCell)
    expect(row1Cells.at(0).text()).toBe('Statement of Registration')
    expect(row1Cells.at(1).text()).toBe('ab12')
    expect(row1Cells.at(2).text()).toBe('tester 123')
    expect(row1Cells.at(3).text()).toContain('January 24, 20233:09 PM')
    expect(row1Cells.at(4).text()).toBe('$0.00')
    expect(row1Cells.at(5).text()).toBe('25663')
    expect(row1Cells.at(6).text()).toBe('N/A')
    expect(row1Cells.at(7).text()).toBe('Completed  January 24, 2023')
    expect(row1Cells.at(8).text()).toBe('')
    // clear filters is hidden
    expect(wrapper.find('.clear-btn').exists()).toBe(false)
  }, 10000)

  it('shows date picker when date filter clicked', async () => {
    // verify setup
    expect(wrapper.find(DatePicker).isVisible()).toBe(false)
    expect(wrapper.find('.date-filter').exists()).toBe(true)
    // simulate click (trigger click not working in this test)
    wrapper.vm.showDatePicker = true
    await Vue.nextTick()
    expect(wrapper.find(DatePicker).isVisible()).toBe(true)
  }, 10000)
})
