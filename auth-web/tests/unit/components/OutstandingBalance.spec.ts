import { createLocalVue, mount } from '@vue/test-utils'
import CommonUtils from '@/util/common-util'
import OutstandingBalances from '@/components/pay/OutstandingBalances.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import can from '@/directives/can'
import { useOrgStore } from '@/stores'
import { StatementListResponse, StatementsSummary } from '@/models/statement'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('OutstandingBalances.vue', () => {
  let wrapper: any
  const localVue = createLocalVue()
  const orgStore = useOrgStore()
  localVue.directive('can', can)
  const vuetify = new Vuetify({})
  let statementsResponse: any


  beforeEach(async () => {
    statementsResponse = {
      items: [
        {
          'amountOwing': 351.5,
          'createdOn': '2023-12-02',
          'frequency': 'MONTHLY',
          'fromDate': '2023-11-01',
          'id': 1,
          'isInterimStatement': false,
          'isOverdue': false,
          'notificationDate': null,
          'paymentMethods': [
            'EFT'
          ],
          'toDate': '2023-11-30'
        },
        {
          'amountOwing': 150.0,
          'createdOn': '2024-01-01',
          'frequency': 'MONTHLY',
          'fromDate': '2023-12-01',
          'id': 2,
          'isInterimStatement': false,
          'isOverdue': false,
          'notificationDate': null,
          'paymentMethods': [
            'EFT'
          ],
          'toDate': '2023-12-31'
        }
      ],
      'limit': 100,
      'page': 1,
      'total': 1
      }
    orgStore.getStatementsList = async (_, __) => {
      return Promise.resolve(statementsResponse as any)
    }

    orgStore.getStatementsSummary = async (orgId) => {
      return Promise.resolve({
        oldestDueDate: '2025-01-01',
        totalDue: 50,
        totalInvoiceDue: 50
      })
    }

    orgStore.statementsSummary.totalInvoiceDue = 50

    wrapper = mount(OutstandingBalances, {
      propsData: {
        statementSummary: { 'oldestDueDate': '2023-12-01', 'totalDue': 351.5, 'totalInvoiceDue': 50.0 }
      },
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

  it('is a Vue instance', () => {
    const $t = () => ''
    wrapper = mount(OutstandingBalances, {
      localVue,
      vuetify,
      propsData: {
        statementSummary: { 'oldestDueDate': '2023-12-01', 'totalDue': 351.5, 'totalInvoiceDue': 50.0 }
      },
      mocks: { $t
      }
    })
    expect(wrapper.vm).toBeTruthy()
  })

  it('validate amount owing details', async () => {
    // Change the prop value
    const propsData = {
      statementSummary: {
        'oldestDueDate': '2023-12-01',
        'totalDue': 551.5,
        'totalInvoiceDue': 50.0
      }
    }
    await wrapper.setProps(propsData)
    await wrapper.vm.$nextTick()

    expect(wrapper.find('[data-test="caution-box-details"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="cc-payment-card"]').exists()).toBe(true)
    expect(wrapper.find('.amount-owing-details-card').exists()).toBe(true)

    const statementRows = wrapper.findAll('[data-test="statement-row"]')
    expect(statementRows).toHaveLength(statementsResponse.items.length)

    for (let i = 0; i < statementsResponse.items.length; i++) {
      const columns = statementRows.at(i).findAll('.statement-col')
      const item = statementsResponse.items[i]
      expect(columns).toHaveLength(2)
      expect(columns.at(0).text()).toBe(CommonUtils.formatStatementString(item.fromDate, item.toDate))
      expect(columns.at(1).text()).toBe(CommonUtils.formatAmount(item.amountOwing))
    }

    expect(wrapper.find('[data-test="total-other-owing"]').text())
      .toBe(CommonUtils.formatAmount(propsData.statementSummary.totalInvoiceDue))

    expect(wrapper.find('[data-test="total-amount-due"]').text())
      .toBe(CommonUtils.formatAmount(propsData.statementSummary.totalDue))
  })
})
