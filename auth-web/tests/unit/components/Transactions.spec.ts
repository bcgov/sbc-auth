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

  // Helper function to setup wrapper with given credit values
  const setupWrapperWithCredits = async (obCredit: string | undefined | null, padCredit: string | undefined | null, paymentMethod: string) => {
    const orgPaymentDetails = createOrgPaymentDetails({
      obCredit: obCredit?.toString(),
      padCredit: padCredit?.toString(),
      paymentMethod
    })
    const setup = await mountTransactionsWithStore(orgPaymentDetails, Account.PREMIUM, transactionResponse)
    wrapper = setup.wrapper
    sandbox = setup.sandbox
    await Vue.nextTick()
  }

  describe('Credit display and calculations', () => {
    it('should handle obCredit and padCredit display scenarios', async () => {
      // Test obCredit display
      await setupWrapperWithCredits('50.00', '0', 'ONLINE_BANKING')
      expect(wrapper.find('.credit-header-row').exists()).toBe(true)
      expect(wrapper.text()).toContain('Account Credit Available:')
      expect(wrapper.text()).toContain('Online Banking')
      expect(wrapper.text()).toContain('$50.00')
      expect(wrapper.vm.obCredit).toBe(50.00)
      expect(wrapper.vm.hasObCredit).toBe(true)
      expect(wrapper.vm.hasPadCredit).toBe(false)

      await setupWrapperWithCredits('0', '100.00', 'PAD')
      expect(wrapper.find('.credit-header-row').exists()).toBe(true)
      expect(wrapper.text()).toContain('Account Credit Available:')
      expect(wrapper.text()).toContain('Pre-Authorized Debit')
      expect(wrapper.text()).toContain('$100.00')
      expect(wrapper.vm.padCredit).toBe(100.00)
      expect(wrapper.vm.hasObCredit).toBe(false)
      expect(wrapper.vm.hasPadCredit).toBe(true)

      await setupWrapperWithCredits('75.00', '125.00', 'ONLINE_BANKING')
      expect(wrapper.find('.credit-header-row').exists()).toBe(true)
      expect(wrapper.text()).toContain('Account Credit Available:')
      expect(wrapper.text()).toContain('Online Banking')
      expect(wrapper.text()).toContain('$75.00')
      expect(wrapper.text()).toContain('Pre-Authorized Debit')
      expect(wrapper.text()).toContain('$125.00')
      expect(wrapper.vm.obCredit).toBe(75.00)
      expect(wrapper.vm.padCredit).toBe(125.00)
      expect(wrapper.vm.hasObCredit).toBe(true)
      expect(wrapper.vm.hasPadCredit).toBe(true)
    })

    it('should handle zero and null credit scenarios', async () => {
      await setupWrapperWithCredits('0', '25.00', 'PAD')
      expect(wrapper.find('.credit-header-row').exists()).toBe(true)
      expect(wrapper.text()).toContain('Account Credit Available:')
      expect(wrapper.text()).not.toContain('Online Banking')
      expect(wrapper.text()).toContain('Pre-Authorized Debit')
      expect(wrapper.text()).toContain('$25.00')
      expect(wrapper.vm.obCredit).toBe(0)
      expect(wrapper.vm.hasObCredit).toBe(false)

      await setupWrapperWithCredits('50.00', '0', 'ONLINE_BANKING')
      expect(wrapper.find('.credit-header-row').exists()).toBe(true)
      expect(wrapper.text()).toContain('Account Credit Available:')
      expect(wrapper.text()).not.toContain('Pre-Authorized Debit')
      expect(wrapper.text()).toContain('Online Banking')
      expect(wrapper.text()).toContain('$50.00')
      expect(wrapper.vm.padCredit).toBe(0)
      expect(wrapper.vm.hasPadCredit).toBe(false)

      await setupWrapperWithCredits('0', '0', 'CC')
      expect(wrapper.find('.credit-header-row').exists()).toBe(false)
      expect(wrapper.text()).not.toContain('Account Credit Available:')
    })

    it('should handle undefined and null credit values', async () => {
      await setupWrapperWithCredits(undefined, '0', 'CC')
      expect(wrapper.vm.obCredit).toBe(0)
      expect(wrapper.vm.hasObCredit).toBe(false)

      await setupWrapperWithCredits(null, '0', 'CC')
      expect(wrapper.vm.obCredit).toBe(0)
      expect(wrapper.vm.hasObCredit).toBe(false)

      await setupWrapperWithCredits('0', undefined, 'CC')
      expect(wrapper.vm.padCredit).toBe(0)
      expect(wrapper.vm.hasPadCredit).toBe(false)

      await setupWrapperWithCredits('0', null, 'CC')
      expect(wrapper.vm.padCredit).toBe(0)
      expect(wrapper.vm.hasPadCredit).toBe(false)
    })

    it('should handle string credit values and edge cases', async () => {
      await setupWrapperWithCredits('75.50', '0', 'ONLINE_BANKING')
      expect(wrapper.vm.obCredit).toBe(75.50)
      expect(wrapper.vm.hasObCredit).toBe(true)
      expect(wrapper.text()).toContain('$75.50')

      await setupWrapperWithCredits('0', '250.75', 'PAD')
      expect(wrapper.vm.padCredit).toBe(250.75)
      expect(wrapper.vm.hasPadCredit).toBe(true)
      expect(wrapper.text()).toContain('$250.75')

      await setupWrapperWithCredits('50.00', '0', 'ONLINE_BANKING')
      expect(wrapper.find('.credit-details').exists()).toBe(true)
      expect(wrapper.text()).toContain('Credit for different payment methods are not transferable')
      expect(wrapper.text()).toContain('Product and Payment page')
    })
  })

  describe('Show credit prop functionality', () => {
    it('should handle showCredit prop scenarios', async () => {
      await setupWrapperWithCredits('50.00', '25.00', 'ONLINE_BANKING')

      wrapper.setProps({ showCredit: false })
      await Vue.nextTick()
      expect(wrapper.find('.credit-header-row').exists()).toBe(false)
      expect(wrapper.text()).not.toContain('Account Credit Available:')

      wrapper.setProps({ showCredit: true })
      await Vue.nextTick()
      expect(wrapper.find('.credit-header-row').exists()).toBe(true)
      expect(wrapper.text()).toContain('Account Credit Available:')
    })
  })
})
