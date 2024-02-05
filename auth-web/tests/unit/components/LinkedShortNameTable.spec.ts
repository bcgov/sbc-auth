import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import { BaseVDataTable } from '@/components'
import LinkedShortNameTableVue from '@/components/pay/LinkedShortNameTable.vue'
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
const { header, headerTitles, itemRow, itemCell } = baseVdataTable
const headers = ['Bank Short Name', 'Account Name', 'Branch Name', 'Account Number', 'Actions']

describe('LinkedShortNameTable.vue', () => {
  setupIntersectionObserverMock()
  let wrapper: Wrapper<any>
  let sandbox: any
  let localVue: VueConstructor<any>
  let linkedShortNameResponse: any

  beforeEach(async () => {
    localVue = createLocalVue()
    linkedShortNameResponse = {
      items: [
        {
          shortName: 'RCPV',
          accountName: 'RCPV',
          accountBranch: 'Saanich',
          accountId: '3199',
          id: 1
        },
        {
          shortName: 'SHORT NAME',
          accountName: 'SUPER ACCOUNT',
          accountBranch: 'OUT THERE',
          accountId: '3135',
          id: 2
        },
        {
          shortName: 'little name',
          accountName: 'BIG ACCOUNT',
          accountBranch: 'VICTORIA',
          accountId: '6000',
          id: 3
        },
        {
          shortName: 'WOW',
          accountName: 'BOO',
          accountBranch: '',
          accountId: '911',
          id: 4
        }
      ],
      total: 4
    }

    sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'get')
    get.returns(Promise.resolve(resolve => resolve({ data: linkedShortNameResponse })))

    wrapper = mount(LinkedShortNameTableVue, {
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

  it('Renders linked short name table with correct contents', async () => {
    expect(wrapper.find('#table-title-cell').text()).toContain('Linked Bank Short Names (4)')

    // verify table
    expect(wrapper.findComponent(BaseVDataTable).exists()).toBe(true)
    expect(wrapper.findComponent(BaseVDataTable).find(header).exists()).toBe(true)
    expect(wrapper.find('#linked-bank-short-names').exists()).toBe(true)
    expect(wrapper.find('.v-data-table__wrapper').exists()).toBe(true)
    const titles = wrapper.findComponent(BaseVDataTable).findAll(headerTitles)
    expect(titles.length).toBe(headers.length)
    for (let i = 0; i < headers.length; i++) {
      expect(titles.at(i).text()).toBe(headers[i])
    }

    // verify data
    const itemRows = wrapper.findComponent(BaseVDataTable).findAll(itemRow)
    expect(itemRows.length).toBe(linkedShortNameResponse.items.length)
    for (let i = 0; i < linkedShortNameResponse.items.length; i++) {
      const columns = itemRows.at(i).findAll(itemCell)
      expect(columns.at(0).text()).toBe(linkedShortNameResponse.items[i].shortName)
      expect(columns.at(1).text()).toBe(linkedShortNameResponse.items[i].accountName)
      expect(columns.at(2).text()).toBe(linkedShortNameResponse.items[i].accountBranch)
      expect(columns.at(3).text()).toBe(linkedShortNameResponse.items[i].accountId)
    }
  })
})
