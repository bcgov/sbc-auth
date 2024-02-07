import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import { BaseVDataTable } from '@/components'
import CommonUtils from '@/util/common-util'
import ShortNameTransactions from '@/components/pay/eft/ShortNameTransactions.vue'
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
const headers = ['Payment Received Date', 'Amount']

describe('ShortNameTransactions.vue', () => {
  setupIntersectionObserverMock()
  let wrapper: Wrapper<any>
  let sandbox: any
  let localVue: VueConstructor<any>
  let transactionsResponse: any

  beforeEach(async () => {
    localVue = createLocalVue()
    transactionsResponse = {
      items: [
        {
          depositAmount: 0.04,
          depositDate: '2024-01-17T14:05:23',
          id: 10,
          shortNameId: 2,
          transactionDate: '2024-01-17T14:05:33'
        },
        {
          depositAmount: 0.03,
          depositDate: '2024-01-16T14:05:23',
          id: 9,
          shortNameId: 2,
          transactionDate: '2024-01-16T14:05:33'
        },
        {
          depositAmount: 0.02,
          depositDate: '2024-01-15T14:05:23',
          id: 8,
          shortNameId: 2,
          transactionDate: '2024-01-15T14:05:33'
        },
        {
          depositAmount: 0.01,
          depositDate: '2024-01-14T14:05:23',
          id: 7,
          shortNameId: 2,
          transactionDate: '2024-01-14T14:05:33'
        },
        {
          depositAmount: 151.5,
          depositDate: '2024-01-13T14:05:23',
          id: 6,
          shortNameId: 2,
          transactionDate: '2024-01-13T14:05:33'
        }
      ],
      limit: 5,
      page: 1,
      remainingCredit: 0,
      total: 5
    }

    sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'get')
    get.returns(new Promise(resolve => resolve({ data: transactionsResponse })))

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

    expect(wrapper.find('#table-title-cell').text()).toContain('Payments Received from SHORTNAME (5)')

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
    expect(itemRows.length).toBe(transactionsResponse.items.length)
    for (let i = 0; i < transactionsResponse.items.length; i++) {
      const columns = itemRows.at(i).findAll(itemCell)
      expect(columns.at(0).text()).toBe(
        CommonUtils.formatDisplayDate(transactionsResponse.items[i].transactionDate, 'MMMM DD, YYYY'))
      expect(columns.at(1).text()).toBe(
        CommonUtils.formatAmount(transactionsResponse.items[i].depositAmount))
    }
  })
})
