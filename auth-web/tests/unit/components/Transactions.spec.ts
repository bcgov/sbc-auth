import '../test-utils/composition-api-setup' // important to import this first
import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import { MembershipType } from '@/models/Organization'
import { Transactions } from '@/components/auth/account-settings/transaction'
import TransactionsDataTable from '@/components/auth/account-settings/transaction/TransactionsDataTable.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import { axios } from '@/util/http-util'
import flushPromises from 'flush-promises'
import sinon from 'sinon'
import { transactionResponse } from '../test-utils'
import { useOrgStore } from '@/stores/org'

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Transactions tests', () => {
  let wrapper: Wrapper<any>
  let sandbox: any

  const config = {
    AUTH_API_URL: 'https://localhost:8080/api/v1/app',
    PAY_API_URL: 'https://pay-api.gov.bc.ca/api/v1'
  }
  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(async () => {
    const localVue = createLocalVue()
    const orgStore = useOrgStore()
    orgStore.currentOrgPaymentDetails = { accountId: 123 } as any
    orgStore.currentOrganization = { id: 123 } as any
    orgStore.currentMembership = { membershipTypeCode: MembershipType.Admin } as any
    orgStore.getOrgPayments = vi.fn(() => { return { credit: 0 } }) as any

    // stub get transactions get call
    sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'post')
    get.returns(Promise.resolve({ data: transactionResponse }))

    wrapper = mount(Transactions, {
      localVue,
      vuetify
    })
    await flushPromises()
  }, 50000)

  afterEach(() => {
    wrapper.destroy()
    sandbox.restore()
  })

  it('renders transaction with child components', () => {
    expect(wrapper.find(Transactions).exists()).toBe(true)
    expect(wrapper.find(TransactionsDataTable).exists()).toBe(true)
    expect(wrapper.find('.view-header__title').exists()).toBe(false)
    expect(wrapper.find('.cad-credit').exists()).toBe(false)
    expect(wrapper.find('.credit-details').exists()).toBe(false)
    expect(wrapper.find("[data-test='btn-export-csv']").exists()).toBe(true)
    expect(wrapper.find('.column-selections').exists()).toBe(true)
    // defaults to extended false
    expect(wrapper.vm.extended).toBe(false)
    expect(wrapper.find(TransactionsDataTable).props().extended).toBe(false)
  })

  it('shows credit message when credit updated', async () => {
    wrapper.vm.credit = 1
    await Vue.nextTick()
    expect(wrapper.find('.cad-credit').exists()).toBe(true)
    expect(wrapper.find('.credit-details').exists()).toBe(true)
    expect(wrapper.find('.cad-credit').text()).toContain('CAD')
    expect(wrapper.find('.credit-details').text()).toContain('$1.00')
  })

  it('shows title when given', async () => {
    expect(wrapper.find('.view-header__title').exists()).toBe(false)
    const titleText = 'title'
    wrapper.setProps({ title: titleText })
    await Vue.nextTick()
    expect(wrapper.find('.view-header__title').text()).toBe(titleText)
  })

  it('hides export button when needed', async () => {
    expect(wrapper.find("[data-test='btn-export-csv']").exists()).toBe(true)
    wrapper.setProps({ showExport: false })
    await Vue.nextTick()
    expect(wrapper.find("[data-test='btn-export-csv']").exists()).toBe(false)
  })

  it('defaults', async () => {
    expect(wrapper.find("[data-test='btn-export-csv']").exists()).toBe(true)
    wrapper.setProps({ showExport: false })
    await Vue.nextTick()
    expect(wrapper.find("[data-test='btn-export-csv']").exists()).toBe(false)
  })
})
