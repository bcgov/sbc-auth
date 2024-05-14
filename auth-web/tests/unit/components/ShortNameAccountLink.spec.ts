import { createLocalVue, mount } from '@vue/test-utils'
import { BaseVDataTable } from '@/components'
import CommonUtils from '@/util/common-util'
import ShortNameAccountLink from '@/components/pay/eft/ShortNameAccountLink.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import { axios } from '@/util/http-util'
import { baseVdataTable } from './../test-utils/test-data/baseVdata'
import can from '@/directives/can'
import sinon from 'sinon'

Vue.use(Vuetify)
Vue.use(VueRouter)

// Selectors
const { header, headerTitles, itemRow, itemCell } = baseVdataTable
const headers = ['Linked Account', 'Branch', 'Latest Statement Number', 'Amount Owing', 'Actions']

describe('ShortNameAccountLink.vue', () => {
  let wrapper: any
  const localVue = createLocalVue()
  localVue.directive('can', can)
  const vuetify = new Vuetify({})
  let sandbox: any
  let linksResponse: any

  beforeEach(async () => {
    linksResponse = {
      items: [
        {
          'accountBranch': '',
          'accountId': '3175',
          'accountName': "Ody's Dev Test 3",
          'amountOwing': 0.0,
          'id': 103,
          'shortNameId': 2,
          'statementId': 5407406,
          'statusCode': 'LINKED'
        },
        {
          'accountBranch': 'Test Branch',
          'accountId': '3202',
          'accountName': 'Odysseus Chiu',
          'amountOwing': 51.5,
          'id': 45,
          'shortNameId': 2,
          'statementId': 5407509,
          'statusCode': 'LINKED'
        }
      ],
      'limit': 5,
      'page': 1,
      'total': 3
    }

    sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'get')
    get.returns(new Promise(resolve => resolve({ data: linksResponse })))

    wrapper = mount(ShortNameAccountLink, {
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

  it('is a Vue instance', () => {
    const $t = () => ''
    wrapper = mount(ShortNameAccountLink, {
      localVue,
      vuetify,
      propsData: {
        shortNameDetails: { shortName: 'SHORTNAME' }
      },
      mocks: { $t
      }
    })
    expect(wrapper.vm).toBeTruthy()
  })

  it('validate shortname is unlinked', () => {
    const $t = () => ''
    wrapper = mount(ShortNameAccountLink, {
      localVue,
      vuetify,
      propsData: {
        shortNameDetails: { shortName: 'SHORTNAME' }
      },
      mocks: { $t
      }
    })
    expect(wrapper.find('.unlinked-text').text())
      .toContain('This short name is not linked with an account.')
    expect(wrapper.find('#link-shortname-btn').exists()).toBe(true)
  })

  it('validate shortname is linked', async () => {
    // Change the prop value
    await wrapper.setProps({ shortNameDetails: { id: 1, shortName: 'SHORTNAME' } })
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.linked-text').text())
      .toContain(`Link a New Account`)
    expect(wrapper.find('#link-shortname-btn').exists()).toBe(true)

    // verify table
    expect(wrapper.findComponent(BaseVDataTable).exists()).toBe(true)
    expect(wrapper.findComponent(BaseVDataTable).find(header).exists()).toBe(true)
    expect(wrapper.find('#eft-account-linking-table').exists()).toBe(true)
    expect(wrapper.find('.v-data-table__wrapper').exists()).toBe(true)
    const titles = wrapper.findComponent(BaseVDataTable).findAll(headerTitles)
    expect(titles.length).toBe(headers.length)
    for (let i = 0; i < headers.length; i++) {
      expect(titles.at(i).text()).toBe(headers[i])
    }

    await wrapper.vm.$nextTick()

    // verify data
    const itemRows = wrapper.findComponent(BaseVDataTable).findAll(itemRow)
    expect(itemRows.length).toBe(linksResponse.items.length)
    for (let i = 0; i < linksResponse.items.length; i++) {
      const columns = itemRows.at(i).findAll(itemCell)
      expect(columns.at(0).text()).toContain(linksResponse.items[i].accountId)
      expect(columns.at(0).text()).toContain(linksResponse.items[i].accountName)
      expect(columns.at(1).text()).toBe(linksResponse.items[i].accountBranch)
      expect(columns.at(2).text()).toBe(linksResponse.items[i].statementId.toString())
      expect(columns.at(3).text()).toBe(
        CommonUtils.formatAmount(linksResponse.items[i].amountOwing))
    }
  })
})
