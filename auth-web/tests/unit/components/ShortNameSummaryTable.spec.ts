import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import { BaseVDataTable } from '@/components'
import CommonUtils from '@/util/common-util'
import ShortNameSummaryTableVue from '@/components/pay/ShortNameSummaryTable.vue'
import { VueConstructor } from 'vue'
import Vuetify from 'vuetify'
import { axios } from '@/util/http-util'
import { baseVdataTable } from './../test-utils/test-data/baseVdata'
import { setupIntersectionObserverMock } from '../util/helper-functions'
import sinon from 'sinon'

sessionStorage.setItem('AUTH_API_CONFIG', JSON.stringify({
  AUTH_API_URL: 'https://localhost:8080/api/v1/11',
  PAY_API_URL: 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
}))

const vuetify = new Vuetify({})
// Selectors
const header = baseVdataTable.header
const headerTitles = baseVdataTable.headerTitles
const itemRow = baseVdataTable.itemRow
const itemCell = baseVdataTable.itemCell

const headers = [
  'Short Name',
  'Last Payment Received Date',
  'Unsettled Amount',
  'Number of Linked Accounts',
  'Actions'
]

describe('ShortNameSummaryTable.vue', () => {
  setupIntersectionObserverMock()
  let wrapper: Wrapper<any>
  let localVue: VueConstructor<any>
  let shortNameSummaryResponse: any

  beforeEach(async () => {
    localVue = createLocalVue()
    shortNameSummaryResponse = {
      items: [
        {
          creditsRemaining: 0.0,
          id: 142,
          lastPaymentReceivedDate: '2024-01-28T10:00:00',
          linkedAccountsCount: 0,
          shortName: 'SNAME129'
        },
        {
          creditsRemaining: 151.5,
          id: 123,
          lastPaymentReceivedDate: '2024-01-28T10:00:00',
          linkedAccountsCount: 0,
          shortName: 'SNAME110'
        },
        {
          creditsRemaining: 204.0,
          id: 158,
          lastPaymentReceivedDate: '2024-01-27T10:00:00',
          linkedAccountsCount: 1,
          shortName: 'SNAME145'
        },
        {
          creditsRemaining: 50.25,
          id: 156,
          lastPaymentReceivedDate: '2024-01-27T10:00:00',
          linkedAccountsCount: 1,
          shortName: 'SNAME143'
        },
        {
          creditsRemaining: 0.0,
          id: 134,
          lastPaymentReceivedDate: '2023-11-24T10:00:00',
          linkedAccountsCount: 2,
          shortName: 'SNAME121'
        }
      ],
      total: 5
    }

    const sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'get')
    get.returns(new Promise(resolve => resolve({ data: shortNameSummaryResponse })))

    wrapper = mount(ShortNameSummaryTableVue, {
      localVue,
      vuetify
    })
    await wrapper.vm.$nextTick()
  })

  afterEach(() => {
    wrapper.destroy()
    sessionStorage.clear()

    vi.resetModules()
    vi.clearAllMocks()
  })

  it('Renders short name summary table with correct contents', async () => {
    expect(wrapper.find('#table-title-cell').text()).toContain('All Short Names  (5)')

    // verify table
    expect(wrapper.findComponent(BaseVDataTable).exists()).toBe(true)
    expect(wrapper.findComponent(BaseVDataTable).find(header).exists()).toBe(true)
    expect(wrapper.find('#short-name-summaries').exists()).toBe(true)
    expect(wrapper.find('.v-data-table__wrapper').exists()).toBe(true)
    const titles = wrapper.findComponent(BaseVDataTable).findAll(headerTitles)
    expect(titles.length).toBe(headers.length)
    for (let i = 0; i < headers.length; i++) {
      expect(titles.at(i).text()).toBe(headers[i])
    }

    // verify data
    const itemRows = wrapper.findComponent(BaseVDataTable).findAll(itemRow)
    expect(itemRows.length).toBe(shortNameSummaryResponse.items.length)
    for (let i = 0; i < shortNameSummaryResponse.items.length; i++) {
      const columns = itemRows.at(i).findAll(itemCell)
      expect(columns.at(0).text()).toBe(shortNameSummaryResponse.items[i].shortName)
      expect(columns.at(1).text()).toBe(
        CommonUtils.formatDisplayDate(shortNameSummaryResponse.items[i].lastPaymentReceivedDate, 'MMMM DD, YYYY'))
      expect(columns.at(2).text()).toBe(
        CommonUtils.formatAmount(shortNameSummaryResponse.items[i].creditsRemaining))
      expect(columns.at(3).text()).toBe(shortNameSummaryResponse.items[i].linkedAccountsCount.toString())
    }
  })
})
