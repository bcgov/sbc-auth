import '../test-utils/composition-api-setup'
import { createOrgPaymentDetails, mountTransactionsWithStore, restoreSandbox } from '../test-utils/vue-test-utils'
import { Account } from '@/util/constants'
import Transactions from '@/components/auth/account-settings/transaction/Transactions.vue'
import TransactionsDataTable from '@/components/auth/account-settings/transaction/TransactionsDataTable.vue'
import Vue from 'vue'
import { transactionResponse } from '../test-utils/test-data/transaction'

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

const allowedAccountTypes = [Account.PREMIUM, Account.STAFF, Account.SBC_STAFF]

describe('Transactions account type tests', () => {
  let wrapper: any
  let sandbox: any

  const config = {
    AUTH_API_URL: 'https://localhost:8080/api/v1/app',
    PAY_API_URL: 'https://pay-api.gov.bc.ca/api/v1'
  }
  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  afterEach(() => {
    if (wrapper) wrapper.destroy()
    restoreSandbox(sandbox)
  })

  allowedAccountTypes.forEach((accountType) => {
    it(`renders transactions for account type ${accountType}`, async () => {
      const orgPaymentDetails = createOrgPaymentDetails()
      const setup = await mountTransactionsWithStore(orgPaymentDetails, accountType, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      expect(wrapper.findComponent(Transactions).exists()).toBe(true)
      expect(wrapper.findComponent(TransactionsDataTable).exists()).toBe(true)
      expect(wrapper.find('.view-header__title').exists()).toBe(false)
      expect(wrapper.find('.cad-credit').exists()).toBe(false)
      expect(wrapper.find('.credit-details').exists()).toBe(false)
      expect(wrapper.find("[data-test='btn-export-csv']").exists()).toBe(true)
      expect(wrapper.find('.column-selections').exists()).toBe(true)
      // defaults to extended false
      expect(wrapper.vm.extended).toBe(false)
      expect(wrapper.findComponent(TransactionsDataTable).props().extended).toBe(false)
    })

    it('shows credit message when credit updated', async () => {
      const orgPaymentDetails = createOrgPaymentDetails()
      const setup = await mountTransactionsWithStore(orgPaymentDetails, accountType, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      wrapper.vm.obCredit = 1
      await Vue.nextTick()
      expect(wrapper.find('.credit-details').exists()).toBe(true)
      expect(wrapper.find('.credit-method-amount').text()).toContain('$1.00')
    })

    it('shows title when given', async () => {
      const orgPaymentDetails = createOrgPaymentDetails()
      const setup = await mountTransactionsWithStore(orgPaymentDetails, accountType, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      expect(wrapper.find('.view-header__title').exists()).toBe(false)
      const titleText = 'title'
      wrapper.setProps({ title: titleText })
      await Vue.nextTick()
      expect(wrapper.find('.view-header__title').text()).toBe(titleText)
    })

    it('hides export button when needed', async () => {
      const orgPaymentDetails = createOrgPaymentDetails()
      const setup = await mountTransactionsWithStore(orgPaymentDetails, accountType, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      expect(wrapper.find("[data-test='btn-export-csv']").exists()).toBe(true)
      wrapper.setProps({ showExport: false })
      await Vue.nextTick()
      expect(wrapper.find("[data-test='btn-export-csv']").exists()).toBe(false)
    })

    it('defaults', async () => {
      const orgPaymentDetails = createOrgPaymentDetails()
      const setup = await mountTransactionsWithStore(orgPaymentDetails, accountType, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      expect(wrapper.find("[data-test='btn-export-csv']").exists()).toBe(true)
      wrapper.setProps({ showExport: false })
      await Vue.nextTick()
      expect(wrapper.find("[data-test='btn-export-csv']").exists()).toBe(false)
    })
  })
})

describe('Transactions obCredit and padCredit functionality', () => {
  let wrapper: any
  let sandbox: any

  const config = {
    AUTH_API_URL: 'https://localhost:8080/api/v1/app',
    PAY_API_URL: 'https://pay-api.gov.bc.ca/api/v1'
  }
  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  afterEach(() => {
    if (wrapper) wrapper.destroy()
    restoreSandbox(sandbox)
  })

  describe('obCredit display', () => {
    it('should display obCredit when available', async () => {
      const orgPaymentDetails = createOrgPaymentDetails({
        obCredit: '50.00',
        padCredit: '0',
        paymentMethod: 'ONLINE_BANKING'
      })
      const setup = await mountTransactionsWithStore(orgPaymentDetails, Account.PREMIUM, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      await Vue.nextTick()
      expect(wrapper.find('.credit-header-row').exists()).toBe(true)
      expect(wrapper.text()).toContain('Account Credit Available:')
      expect(wrapper.text()).toContain('Online Banking')
      expect(wrapper.text()).toContain('$50.00')
    })

    it('should not display obCredit when zero', async () => {
      const orgPaymentDetails = createOrgPaymentDetails({
        obCredit: '0',
        padCredit: '25.00',
        paymentMethod: 'PAD'
      })
      const setup = await mountTransactionsWithStore(orgPaymentDetails, Account.PREMIUM, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      await Vue.nextTick()
      expect(wrapper.find('.credit-header-row').exists()).toBe(true)
      expect(wrapper.text()).toContain('Account Credit Available:')
      expect(wrapper.text()).not.toContain('Online Banking')
      expect(wrapper.text()).toContain('Pre-Authorized Debit')
      expect(wrapper.text()).toContain('$25.00')
    })

    it('should handle undefined obCredit', async () => {
      const orgPaymentDetails = createOrgPaymentDetails({
        obCredit: undefined,
        padCredit: '0',
        paymentMethod: 'CC'
      })
      const setup = await mountTransactionsWithStore(orgPaymentDetails, Account.PREMIUM, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      await Vue.nextTick()
      expect(wrapper.vm.obCredit).toBe(0)
      expect(wrapper.vm.hasObCredit).toBe(false)
    })

    it('should handle null obCredit', async () => {
      const orgPaymentDetails = createOrgPaymentDetails({
        obCredit: null,
        padCredit: '0',
        paymentMethod: 'CC'
      })
      const setup = await mountTransactionsWithStore(orgPaymentDetails, Account.PREMIUM, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      await Vue.nextTick()
      expect(wrapper.vm.obCredit).toBe(0)
      expect(wrapper.vm.hasObCredit).toBe(false)
    })

    it('should handle string obCredit values', async () => {
      const orgPaymentDetails = createOrgPaymentDetails({
        obCredit: '75.50',
        padCredit: '0',
        paymentMethod: 'ONLINE_BANKING'
      })
      const setup = await mountTransactionsWithStore(orgPaymentDetails, Account.PREMIUM, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      await Vue.nextTick()
      expect(wrapper.vm.obCredit).toBe(75.50)
      expect(wrapper.vm.hasObCredit).toBe(true)
      expect(wrapper.text()).toContain('$75.50')
    })
  })

  describe('padCredit display', () => {
    it('should display padCredit when available', async () => {
      const orgPaymentDetails = createOrgPaymentDetails({
        obCredit: '0',
        padCredit: '100.00',
        paymentMethod: 'PAD'
      })
      const setup = await mountTransactionsWithStore(orgPaymentDetails, Account.PREMIUM, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      await Vue.nextTick()
      expect(wrapper.find('.credit-header-row').exists()).toBe(true)
      expect(wrapper.text()).toContain('Account Credit Available:')
      expect(wrapper.text()).toContain('Pre-Authorized Debit')
      expect(wrapper.text()).toContain('$100.00')
    })

    it('should not display padCredit when zero', async () => {
      const orgPaymentDetails = createOrgPaymentDetails({
        obCredit: '50.00',
        padCredit: '0',
        paymentMethod: 'ONLINE_BANKING'
      })
      const setup = await mountTransactionsWithStore(orgPaymentDetails, Account.PREMIUM, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      await Vue.nextTick()
      expect(wrapper.find('.credit-header-row').exists()).toBe(true)
      expect(wrapper.text()).toContain('Account Credit Available:')
      expect(wrapper.text()).not.toContain('Pre-Authorized Debit')
      expect(wrapper.text()).toContain('Online Banking')
      expect(wrapper.text()).toContain('$50.00')
    })

    it('should handle undefined padCredit', async () => {
      const orgPaymentDetails = createOrgPaymentDetails({
        obCredit: '0',
        padCredit: undefined,
        paymentMethod: 'CC'
      })
      const setup = await mountTransactionsWithStore(orgPaymentDetails, Account.PREMIUM, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      await Vue.nextTick()
      expect(wrapper.vm.padCredit).toBe(0)
      expect(wrapper.vm.hasPadCredit).toBe(false)
    })

    it('should handle null padCredit', async () => {
      const orgPaymentDetails = createOrgPaymentDetails({
        obCredit: '0',
        padCredit: null,
        paymentMethod: 'CC'
      })
      const setup = await mountTransactionsWithStore(orgPaymentDetails, Account.PREMIUM, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      await Vue.nextTick()
      expect(wrapper.vm.padCredit).toBe(0)
      expect(wrapper.vm.hasPadCredit).toBe(false)
    })

    it('should handle string padCredit values', async () => {
      const orgPaymentDetails = createOrgPaymentDetails({
        obCredit: '0',
        padCredit: '250.75',
        paymentMethod: 'PAD'
      })
      const setup = await mountTransactionsWithStore(orgPaymentDetails, Account.PREMIUM, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      await Vue.nextTick()
      expect(wrapper.vm.padCredit).toBe(250.75)
      expect(wrapper.vm.hasPadCredit).toBe(true)
      expect(wrapper.text()).toContain('$250.75')
    })
  })

  describe('Both credits display', () => {
    it('should display both obCredit and padCredit when both are available', async () => {
      const orgPaymentDetails = createOrgPaymentDetails({
        obCredit: '75.00',
        padCredit: '125.00',
        paymentMethod: 'ONLINE_BANKING'
      })
      const setup = await mountTransactionsWithStore(orgPaymentDetails, Account.PREMIUM, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      await Vue.nextTick()
      expect(wrapper.find('.credit-header-row').exists()).toBe(true)
      expect(wrapper.text()).toContain('Account Credit Available:')
      expect(wrapper.text()).toContain('Online Banking')
      expect(wrapper.text()).toContain('$75.00')
      expect(wrapper.text()).toContain('Pre-Authorized Debit')
      expect(wrapper.text()).toContain('$125.00')
    })

    it('should hide credit section when no credits are available', async () => {
      const orgPaymentDetails = createOrgPaymentDetails({
        obCredit: '0',
        padCredit: '0',
        paymentMethod: 'CC'
      })
      const setup = await mountTransactionsWithStore(orgPaymentDetails, Account.PREMIUM, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      await Vue.nextTick()
      expect(wrapper.find('.credit-header-row').exists()).toBe(false)
      expect(wrapper.text()).not.toContain('Account Credit Available:')
    })

    it('should show credit details message when credits are available', async () => {
      const orgPaymentDetails = createOrgPaymentDetails({
        obCredit: '50.00',
        padCredit: '0',
        paymentMethod: 'ONLINE_BANKING'
      })
      const setup = await mountTransactionsWithStore(orgPaymentDetails, Account.PREMIUM, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      await Vue.nextTick()
      expect(wrapper.find('.credit-details').exists()).toBe(true)
      expect(wrapper.text()).toContain('Credit for different payment methods are not transferable')
      expect(wrapper.text()).toContain('Product and Payment page')
    })
  })

  describe('Credit calculations', () => {
    it('should calculate hasObCredit correctly', async () => {
      const orgPaymentDetails = createOrgPaymentDetails({
        obCredit: '25.50',
        padCredit: '0',
        paymentMethod: 'ONLINE_BANKING'
      })
      const setup = await mountTransactionsWithStore(orgPaymentDetails, Account.PREMIUM, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      await Vue.nextTick()
      expect(wrapper.vm.hasObCredit).toBe(true)
      expect(wrapper.vm.hasPadCredit).toBe(false)
    })

    it('should calculate hasPadCredit correctly', async () => {
      const orgPaymentDetails = createOrgPaymentDetails({
        obCredit: '0',
        padCredit: '100.00',
        paymentMethod: 'PAD'
      })
      const setup = await mountTransactionsWithStore(orgPaymentDetails, Account.PREMIUM, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      await Vue.nextTick()
      expect(wrapper.vm.hasObCredit).toBe(false)
      expect(wrapper.vm.hasPadCredit).toBe(true)
    })

    it('should calculate both credits correctly', async () => {
      const orgPaymentDetails = createOrgPaymentDetails({
        obCredit: '50.00',
        padCredit: '75.00',
        paymentMethod: 'ONLINE_BANKING'
      })
      const setup = await mountTransactionsWithStore(orgPaymentDetails, Account.PREMIUM, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      await Vue.nextTick()
      expect(wrapper.vm.hasObCredit).toBe(true)
      expect(wrapper.vm.hasPadCredit).toBe(true)
      expect(wrapper.vm.obCredit).toBe(50.00)
      expect(wrapper.vm.padCredit).toBe(75.00)
    })
  })

  describe('Show credit prop', () => {
    it('should hide credit section when showCredit is false', async () => {
      const orgPaymentDetails = createOrgPaymentDetails({
        obCredit: '50.00',
        padCredit: '25.00',
        paymentMethod: 'ONLINE_BANKING'
      })
      const setup = await mountTransactionsWithStore(orgPaymentDetails, Account.PREMIUM, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      wrapper.setProps({ showCredit: false })
      await Vue.nextTick()
      expect(wrapper.find('.credit-header-row').exists()).toBe(false)
      expect(wrapper.text()).not.toContain('Account Credit Available:')
    })

    it('should show credit section when showCredit is true and credits are available', async () => {
      const orgPaymentDetails = createOrgPaymentDetails({
        obCredit: '50.00',
        padCredit: '25.00',
        paymentMethod: 'ONLINE_BANKING'
      })
      const setup = await mountTransactionsWithStore(orgPaymentDetails, Account.PREMIUM, transactionResponse)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      wrapper.setProps({ showCredit: true })
      await Vue.nextTick()
      expect(wrapper.find('.credit-header-row').exists()).toBe(true)
      expect(wrapper.text()).toContain('Account Credit Available:')
    })
  })
})
