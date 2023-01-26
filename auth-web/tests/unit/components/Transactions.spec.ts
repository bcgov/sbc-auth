import '../util/composition-api-setup' // important to import this first
import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import { MembershipType } from '@/models/Organization'
import Transactions from '@/components/auth/account-settings/transaction/Transactions.vue'
import { TransactionsDataTable } from '@/components/auth/account-settings/transaction'
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

describe('TransactionsDataTable tests', () => {
  let wrapper: Wrapper<any>
  let sandbox: any

  const config = {
    AUTH_API_URL: 'https://localhost:8080/api/v1/app',
    PAY_API_URL: 'https://pay-api.gov.bc.ca/api/v1'
  }
  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(async () => {
    const localVue = createLocalVue()
    // store
    const orgModule = {
      namespaced: true,
      state: {
        currentOrgPaymentDetails: { accountId: 123 },
        currentOrganization: { id: 123 },
        currentMembership: { membershipTypeCode: MembershipType.Admin }
      },
      actions: { getOrgPayments: jest.fn(() => { return { credit: 0 } }) }
    }
    const store = new Vuex.Store({ strict: false, modules: { org: orgModule } })

    // stub get transactions get call
    sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'post')
    get.returns(new Promise(resolve => resolve({ data: transactionResponse })))

    wrapper = mount(Transactions, {
      localVue,
      vuetify,
      store
    })
  })

  afterEach(() => {
    wrapper.destroy()
    sandbox.restore()
  })

  it('renders transaction with child components', () => {
    expect(wrapper.find(Transactions).exists()).toBe(true)
    expect(wrapper.find(TransactionsDataTable).exists()).toBe(true)
    expect(wrapper.find('.view-header__title').text()).toBe('Transactions')
    expect(wrapper.find('.cad-credit').exists()).toBe(false)
    expect(wrapper.find('.credit-details').exists()).toBe(false)
    expect(wrapper.find("[data-test='btn-export-csv']").exists()).toBe(true)
    expect(wrapper.find('.column-selections').exists()).toBe(true)
  })

  it('shows credit message when credit updated', async () => {
    wrapper.vm.credit = 1
    await flushPromises()
    expect(wrapper.find('.cad-credit').exists()).toBe(true)
    expect(wrapper.find('.credit-details').exists()).toBe(true)
    expect(wrapper.find('.cad-credit').text()).toContain('CAD')
    expect(wrapper.find('.credit-details').text()).toContain('$1.00')
  })
})
