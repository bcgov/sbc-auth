import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import { BaseVDataTable } from '@/components'
import UnlinkedShortNameTableVue from '@/components/pay/UnlinkedShortNameTable.vue'
import { VueConstructor } from 'vue'
import Vuetify from 'vuetify'
import { axios } from '@/util/http-util'
import { baseVdataTable } from './../test-utils/test-data/baseVdata'
import { setupIntersectionObserverMock } from '../util/helper-functions'
import sinon from 'sinon'
import CommonUtils from '@/util/common-util'

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
  'Bank Short Name',
  'Initial Payment Received Date',
  'Initial Payment Amount',
  'Actions'
]

describe('UnlinkedShortNameTable.vue', () => {
  setupIntersectionObserverMock()
  let wrapper: Wrapper<any>
  let localVue: VueConstructor<any>
  let unlinkedShortNameResponse: any

  beforeEach(async () => {
    localVue = createLocalVue()
    unlinkedShortNameResponse = {
      items: [
        {
          shortName: 'TST1',
          depositDate: '2024-01-28T10:00:00',
          depositAmount: 5,
          id: 1
        },
        {
          shortName: 'TST2',
          depositDate: '2024-01-29T10:00:00',
          depositAmount: 50,
          id: 2
        },
        {
          shortName: 'TST3',
          depositDate: '2024-01-30T10:00:00',
          depositAmount: 133.33,
          id: 3
        },
        {
          shortName: 'TST4',
          depositDate: '2024-01-31T10:00:00',
          depositAmount: 121.21,
          id: 4
        },
        {
          shortName: 'TST5',
          depositDate: '2024-02-01T10:00:00',
          depositAmount: 333.33,
          id: 5
        }
      ],
      total: 5
    }

    const sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'get')
    get.returns(new Promise(resolve => resolve({ data: unlinkedShortNameResponse })))

    wrapper = mount(UnlinkedShortNameTableVue, {
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

  it('Renders unlinked short name table with correct contents', async () => {
    expect(wrapper.find('#table-title-cell').text()).toContain('Unlinked Bank Short Names (5)')

    // verify table
    expect(wrapper.findComponent(BaseVDataTable).exists()).toBe(true)
    expect(wrapper.findComponent(BaseVDataTable).find(header).exists()).toBe(true)
    expect(wrapper.find('#unlinked-bank-short-names').exists()).toBe(true)
    expect(wrapper.find('.v-data-table__wrapper').exists()).toBe(true)
    const titles = wrapper.findComponent(BaseVDataTable).findAll(headerTitles)
    expect(titles.length).toBe(headers.length)
    for (let i = 0; i < headers.length; i++) {
      expect(titles.at(i).text()).toBe(headers[i])
    }

    // verify data
    const itemRows = wrapper.findComponent(BaseVDataTable).findAll(itemRow)
    expect(itemRows.length).toBe(unlinkedShortNameResponse.items.length)
    for (let i = 0; i < unlinkedShortNameResponse.items.length; i++) {
      const columns = itemRows.at(i).findAll(itemCell)
      expect(columns.at(0).text()).toBe(unlinkedShortNameResponse.items[i].shortName)
      expect(columns.at(1).text()).toBe(
        CommonUtils.formatDisplayDate(unlinkedShortNameResponse.items[i].depositDate, 'MMMM DD, YYYY'))
      expect(columns.at(2).text()).toBe(
        CommonUtils.formatAmount(unlinkedShortNameResponse.items[i].depositAmount))
    }
  })
})
