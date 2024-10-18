import { createLocalVue, mount } from '@vue/test-utils'
import { BaseVDataTable } from '@/components'
import { Role } from '@/util/constants'
import ShortNameRefund from '@/components/pay/eft/ShortNameRefund.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import { axios } from '@/util/http-util'
import { baseVdataTable } from './../test-utils/test-data/baseVdata'
import sinon from 'sinon'
import { useUserStore } from '@/stores'

Vue.use(Vuetify)
Vue.use(VueRouter)
// Selectors
const { header, headerTitles, itemRow, itemCell } = baseVdataTable
const headers = ['Initiated By', 'Comment', 'Supplier Record Number', 'Refund Amount', 'Actions']

describe('ShortNameRefund.vue', () => {
  let wrapper
  const localVue = createLocalVue()
  const vuetify = new Vuetify({})
  let sandbox
  let shortNameRefundResponse: any

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    shortNameRefundResponse = [
      {
        'casSupplierNumber': '123456789',
        'comment': 'A test',
        'createdName': 'John Doe',
        'createdOn': '2024-10-17 14:51:27.553425',
        'disbursementDate': '2024-10-17',
        'id': '1',
        'refundAmount': '10',
        'refundEmail': 'john.doe@gov.bc.ca',
        'shortNameId': '243',
        'status': 'PENDING_REFUND'
      }
    ]

    sandbox = sinon.createSandbox()
  })

  afterEach(() => {
    wrapper.destroy()
    sandbox.restore()
  })

  const mountComponent = (role) => {
    const userStore = useUserStore()
    userStore.currentUser = {
      roles: role
    } as any

    return mount(ShortNameRefund, {
      propsData: {
        shortNameDetails: { shortName: null, id: null },
        unsettledAmount: '100.0'
      },
      localVue,
      vuetify
    })
  }

  it('is a Vue instance', async () => {
    wrapper = mountComponent([Role.EftRefundApprover])
    await wrapper.vm.$nextTick()
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the component correctly without data', async () => {
    wrapper = mountComponent([Role.EftRefundApprover])
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.card-title').text()).toContain('Short Name Refund')
    expect(wrapper.find('.card-content span').text())
      .toContain('No refund initiated. SBC Finance can initiate refund if a CAS supplier number is created for the short name.')
  })

  it('renders the component correctly with data', async () => {
    wrapper = mountComponent([Role.EftRefundApprover])
    await wrapper.vm.$nextTick()
    const get = sandbox.stub(axios, 'get')
    get.returns(Promise.resolve({ data: shortNameRefundResponse }))
    await wrapper.setProps({ shortNameDetails: { id: 1, shortName: 'SHORTNAME' }, unsettledAmount: '100.0' })
    await wrapper.vm.$nextTick()
    // table
    expect(wrapper.findComponent(BaseVDataTable).exists()).toBe(true)
    expect(wrapper.findComponent(BaseVDataTable).find(header).exists()).toBe(true)
    // header titles
    const titles = wrapper.findComponent(BaseVDataTable).findAll(headerTitles)
    expect(titles.length).toBe(headers.length)
    expect(titles.at(0).text()).toBe('Initiated By')
    expect(titles.at(1).text()).toBe('Comment')
    expect(titles.at(2).text()).toBe('Supplier Record Number')
    expect(titles.at(3).text()).toBe('Refund Amount')
    expect(titles.at(4).text()).toBe('Actions')
    // table items
    const itemRows = wrapper.findComponent(BaseVDataTable).findAll(itemRow)
    expect(itemRows.length).toBe(shortNameRefundResponse.length)
    // cells
    const row1Cells = itemRows.at(0).findAll(itemCell)
    expect(row1Cells.at(0).text()).toBe('John Doe')
    expect(row1Cells.at(1).text()).toBe('A test')
    expect(row1Cells.at(2).text()).toBe('123456789')
    expect(row1Cells.at(3).findAll('span').at(0).text()).toBe('$10.00')
    expect(row1Cells.at(3).findAll('span').at(1).text()).toBe('View Refund Detail')
    expect(row1Cells.at(4).findAll('button').exists()).toBe(true)
    expect(row1Cells.at(4).findAll('button').at(0).text()).toBe('Decline')
    expect(row1Cells.at(4).findAll('button').at(1).text()).toBe('Approve')
    // without roles
    wrapper.destroy()
    wrapper = mountComponent([])
    await wrapper.vm.$nextTick()
    expect(row1Cells.at(3).findAll('button').exists()).toBe(false)
  })
})
