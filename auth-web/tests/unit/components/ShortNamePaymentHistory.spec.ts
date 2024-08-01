import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import { BaseVDataTable } from '@/components'
import ShortNameTransactions from '@/components/pay/eft/ShortNamePaymentHistory.vue'
import { VueConstructor } from 'vue'
import Vuetify from 'vuetify'
import { axios } from '@/util/http-util'
import { baseVdataTable } from './../test-utils/test-data/baseVdata'
import { setupIntersectionObserverMock } from '../util/helper-functions'
import sinon from 'sinon'

sessionStorage.setItem('AUTH_API_CONFIG', JSON.stringify({
  AUTH_API_URL: 'https://localhost:8080/api/v1',
  PAY_API_URL: 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
}))

const vuetify = new Vuetify({})
// Selectors
const { header, headerTitles, itemRow, itemCell } = baseVdataTable
const headers = ['Date', 'Description', 'Related Statement Number', 'Amount', 'Actions']

describe('ShortNamePaymentHistory.vue', () => {
  setupIntersectionObserverMock()
  let wrapper: Wrapper<any>
  let sandbox: any
  let localVue: VueConstructor<any>
  let historyResponse: any

  beforeEach(async () => {
    localVue = createLocalVue()
    historyResponse = {
      items: [
        {
          'accountBranch': 'Sushi Division',
          'accountId': '3202',
          'accountName': 'Odysseus Chiu',
          'amount': 351.5,
          'historicalId': 5,
          'isProcessing': true,
          'isReversible': false,
          'shortNameBalance': 368.5,
          'shortNameId': 2,
          'statementNumber': 5374449,
          'transactionDate': '2024-08-01T00:01:30.885474',
          'transactionDescription': 'Payment Reversed',
          'transactionType': 'STATEMENT_REVERSE'
        },
        {
          'accountBranch': 'Sushi Division',
          'accountId': '3202',
          'accountName': 'Odysseus Chiu',
          'amount': 131.5,
          'historicalId': 3,
          'isProcessing': true,
          'isReversible': false,
          'shortNameBalance': 368.5,
          'shortNameId': 2,
          'statementNumber': 5455966,
          'transactionDate': '2024-07-31T22:22:31.058547',
          'transactionDescription': 'Statement Paid',
          'transactionType': 'STATEMENT_PAID'
        },
        {
          'accountBranch': 'Sushi Division',
          'accountId': '3202',
          'accountName': 'Odysseus Chiu',
          'amount': 351.5,
          'historicalId': 4,
          'isProcessing': false,
          'isReversible': false,
          'shortNameBalance': 17.0,
          'shortNameId': 2,
          'statementNumber': 5374449,
          'transactionDate': '2024-07-31T00:00:00',
          'transactionDescription': 'Statement Paid',
          'transactionType': 'STATEMENT_PAID'
        }
      ],
      'limit': 5,
      'page': 1,
      'total': 3
    }

    sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'get')
    get.returns(new Promise(resolve => resolve({ data: historyResponse })))

    wrapper = mount(ShortNameTransactions, {
      propsData: {
        shortNameDetails: { shortName: null, id: null }
      },
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

  it('Renders short name transaction table with correct contents', async () => {
    // Change the prop value
    await wrapper.setProps({ shortNameDetails: { id: 1, shortName: 'SHORTNAME' } })
    await wrapper.vm.$nextTick()

    expect(wrapper.find('#table-title-cell').text()).toContain('Short Name Payment History')

    // verify table
    expect(wrapper.findComponent(BaseVDataTable).exists()).toBe(true)
    expect(wrapper.findComponent(BaseVDataTable).find(header).exists()).toBe(true)
    expect(wrapper.find('#eft-transactions-table').exists()).toBe(true)
    expect(wrapper.find('.v-data-table__wrapper').exists()).toBe(true)
    const titles = wrapper.findComponent(BaseVDataTable).findAll(headerTitles)
    expect(titles.length).toBe(headers.length)
    for (let i = 0; i < headers.length; i++) {
      expect(titles.at(i).text()).toBe(headers[i])
    }

    await wrapper.vm.$nextTick()
    // verify data
    const itemRows = wrapper.findComponent(BaseVDataTable).findAll(itemRow)
    expect(itemRows.length).toBe(historyResponse.items.length)
    for (let i = 0; i < historyResponse.items.length; i++) {
      const columns = itemRows.at(i).findAll(itemCell)
      expect(columns.at(0).text()).toBe(wrapper.vm.formatDate(historyResponse.items[i].transactionDate))
      expect(columns.at(1).text()).toContain(historyResponse.items[i].transactionDescription)
      expect(columns.at(2).text()).toBe(historyResponse.items[i].statementNumber
        ? historyResponse.items[i].statementNumber.toString() : '')
      expect(columns.at(3).text()).toContain(
        wrapper.vm.formatTransactionAmount(historyResponse.items[i].amount))
      if (historyResponse.items[i].isReversible) {
        expect(columns.at(4).find("[data-test='reverse-payment-btn']").exists()).toBeTruthy()
      } else {
        expect(columns.at(4).find("[data-test='reverse-payment-btn']").exists()).toBeFalsy()
      }
    }
  })
})
