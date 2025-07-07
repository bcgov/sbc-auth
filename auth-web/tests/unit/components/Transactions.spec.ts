import '../test-utils/composition-api-setup' // important to import this first
import { Account, Permission } from '@/util/constants'
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

const allowedAccountTypes = [Account.PREMIUM, Account.STAFF, Account.SBC_STAFF]

async function beforeEachSetup (wrapper: any, sandbox: any, accountType: Account = Account.PREMIUM, orgPaymentDetails: any = null) {
  const localVue = createLocalVue()
  const orgStore = useOrgStore()

  // Set up default payment details if not provided
  const defaultPaymentDetails = orgPaymentDetails || {
    accountId: 123,
    obCredit: '0',
    padCredit: '0',
    paymentMethod: 'CC'
  }

  orgStore.currentOrgPaymentDetails = defaultPaymentDetails as any
  orgStore.currentOrganization = { id: 123, orgType: accountType } as any
  orgStore.getOrgPayments = vi.fn(() => Promise.resolve(defaultPaymentDetails)) as any
  orgStore.currentMembership = { membershipTypeCode: MembershipType.Admin } as any
  orgStore.permissions = [Permission.TRANSACTION_HISTORY]

  // stub get transactions get call
  sandbox = sinon.createSandbox()
  const get = sandbox.stub(axios, 'post')
  get.returns(Promise.resolve({ data: transactionResponse }))

  wrapper = mount(Transactions, {
    localVue,
    vuetify
  })
  await flushPromises()
  return { wrapper, sandbox }
}

describe('Transactions account type tests', () => {
  let wrapper: Wrapper<any>
  let sandbox: any

  const config = {
    AUTH_API_URL: 'https://localhost:8080/api/v1/app',
    PAY_API_URL: 'https://pay-api.gov.bc.ca/api/v1'
  }
  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  afterEach(() => {
    wrapper.destroy()
    sandbox.restore()
  })

  allowedAccountTypes.forEach(async (accountType) => {
    it(`renders transactions for account type ${accountType}`, async () => {
      const setup = await beforeEachSetup(wrapper, sandbox, accountType)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
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
      const setup = await beforeEachSetup(wrapper, sandbox, accountType)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      wrapper.vm.obCredit = 1
      await Vue.nextTick()
      expect(wrapper.find('.credit-details').exists()).toBe(true)
      expect(wrapper.find('.credit-method-amount').text()).toContain('$1.00')
    })

    it('shows title when given', async () => {
      const setup = await beforeEachSetup(wrapper, sandbox, accountType)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      expect(wrapper.find('.view-header__title').exists()).toBe(false)
      const titleText = 'title'
      wrapper.setProps({ title: titleText })
      await Vue.nextTick()
      expect(wrapper.find('.view-header__title').text()).toBe(titleText)
    })

    it('hides export button when needed', async () => {
      const setup = await beforeEachSetup(wrapper, sandbox, accountType)
      wrapper = setup.wrapper
      sandbox = setup.sandbox
      expect(wrapper.find("[data-test='btn-export-csv']").exists()).toBe(true)
      wrapper.setProps({ showExport: false })
      await Vue.nextTick()
      expect(wrapper.find("[data-test='btn-export-csv']").exists()).toBe(false)
    })

    it('defaults', async () => {
      const setup = await beforeEachSetup(wrapper, sandbox, accountType)
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
  let wrapper: Wrapper<any>
  let sandbox: any

  const config = {
    AUTH_API_URL: 'https://localhost:8080/api/v1/app',
    PAY_API_URL: 'https://pay-api.gov.bc.ca/api/v1'
  }
  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  afterEach(() => {
    wrapper.destroy()
    sandbox.restore()
  })

  describe('obCredit display', () => {
    it('should display obCredit when available', async () => {
      const orgPaymentDetails = {
        accountId: 123,
        obCredit: '50.00',
        padCredit: '0',
        paymentMethod: 'ONLINE_BANKING'
      }
      const setup = await beforeEachSetup(wrapper, sandbox, Account.PREMIUM, orgPaymentDetails)
      wrapper = setup.wrapper
      sandbox = setup.sandbox

      await Vue.nextTick()

      expect(wrapper.find('.credit-header-row').exists()).toBe(true)
      expect(wrapper.text()).toContain('Account Credit Available:')
      expect(wrapper.text()).toContain('Online Banking')
      expect(wrapper.text()).toContain('$50.00')
    })

    it('should not display obCredit when zero', async () => {
      const orgPaymentDetails = {
        accountId: 123,
        obCredit: '0',
        padCredit: '25.00',
        paymentMethod: 'PAD'
      }
      const setup = await beforeEachSetup(wrapper, sandbox, Account.PREMIUM, orgPaymentDetails)
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
      const orgPaymentDetails = {
        accountId: 123,
        obCredit: undefined,
        padCredit: '0',
        paymentMethod: 'CC'
      }
      const setup = await beforeEachSetup(wrapper, sandbox, Account.PREMIUM, orgPaymentDetails)
      wrapper = setup.wrapper
      sandbox = setup.sandbox

      await Vue.nextTick()

      expect(wrapper.vm.obCredit).toBe(0)
      expect(wrapper.vm.hasObCredit).toBe(false)
    })

    it('should handle null obCredit', async () => {
      const orgPaymentDetails = {
        accountId: 123,
        obCredit: null,
        padCredit: '0',
        paymentMethod: 'CC'
      }
      const setup = await beforeEachSetup(wrapper, sandbox, Account.PREMIUM, orgPaymentDetails)
      wrapper = setup.wrapper
      sandbox = setup.sandbox

      await Vue.nextTick()

      expect(wrapper.vm.obCredit).toBe(0)
      expect(wrapper.vm.hasObCredit).toBe(false)
    })

    it('should handle string obCredit values', async () => {
      const orgPaymentDetails = {
        accountId: 123,
        obCredit: '75.50',
        padCredit: '0',
        paymentMethod: 'ONLINE_BANKING'
      }
      const setup = await beforeEachSetup(wrapper, sandbox, Account.PREMIUM, orgPaymentDetails)
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
      const orgPaymentDetails = {
        accountId: 123,
        obCredit: '0',
        padCredit: '100.00',
        paymentMethod: 'PAD'
      }
      const setup = await beforeEachSetup(wrapper, sandbox, Account.PREMIUM, orgPaymentDetails)
      wrapper = setup.wrapper
      sandbox = setup.sandbox

      await Vue.nextTick()

      expect(wrapper.find('.credit-header-row').exists()).toBe(true)
      expect(wrapper.text()).toContain('Account Credit Available:')
      expect(wrapper.text()).toContain('Pre-Authorized Debit')
      expect(wrapper.text()).toContain('$100.00')
    })

    it('should not display padCredit when zero', async () => {
      const orgPaymentDetails = {
        accountId: 123,
        obCredit: '50.00',
        padCredit: '0',
        paymentMethod: 'ONLINE_BANKING'
      }
      const setup = await beforeEachSetup(wrapper, sandbox, Account.PREMIUM, orgPaymentDetails)
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
      const orgPaymentDetails = {
        accountId: 123,
        obCredit: '0',
        padCredit: undefined,
        paymentMethod: 'CC'
      }
      const setup = await beforeEachSetup(wrapper, sandbox, Account.PREMIUM, orgPaymentDetails)
      wrapper = setup.wrapper
      sandbox = setup.sandbox

      await Vue.nextTick()

      expect(wrapper.vm.padCredit).toBe(0)
      expect(wrapper.vm.hasPadCredit).toBe(false)
    })

    it('should handle null padCredit', async () => {
      const orgPaymentDetails = {
        accountId: 123,
        obCredit: '0',
        padCredit: null,
        paymentMethod: 'CC'
      }
      const setup = await beforeEachSetup(wrapper, sandbox, Account.PREMIUM, orgPaymentDetails)
      wrapper = setup.wrapper
      sandbox = setup.sandbox

      await Vue.nextTick()

      expect(wrapper.vm.padCredit).toBe(0)
      expect(wrapper.vm.hasPadCredit).toBe(false)
    })

    it('should handle string padCredit values', async () => {
      const orgPaymentDetails = {
        accountId: 123,
        obCredit: '0',
        padCredit: '250.75',
        paymentMethod: 'PAD'
      }
      const setup = await beforeEachSetup(wrapper, sandbox, Account.PREMIUM, orgPaymentDetails)
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
      const orgPaymentDetails = {
        accountId: 123,
        obCredit: '75.00',
        padCredit: '125.00',
        paymentMethod: 'ONLINE_BANKING'
      }
      const setup = await beforeEachSetup(wrapper, sandbox, Account.PREMIUM, orgPaymentDetails)
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
      const orgPaymentDetails = {
        accountId: 123,
        obCredit: '0',
        padCredit: '0',
        paymentMethod: 'CC'
      }
      const setup = await beforeEachSetup(wrapper, sandbox, Account.PREMIUM, orgPaymentDetails)
      wrapper = setup.wrapper
      sandbox = setup.sandbox

      await Vue.nextTick()

      expect(wrapper.find('.credit-header-row').exists()).toBe(false)
      expect(wrapper.text()).not.toContain('Account Credit Available:')
    })

    it('should show credit details message when credits are available', async () => {
      const orgPaymentDetails = {
        accountId: 123,
        obCredit: '50.00',
        padCredit: '0',
        paymentMethod: 'ONLINE_BANKING'
      }
      const setup = await beforeEachSetup(wrapper, sandbox, Account.PREMIUM, orgPaymentDetails)
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
      const orgPaymentDetails = {
        accountId: 123,
        obCredit: '25.50',
        padCredit: '0',
        paymentMethod: 'ONLINE_BANKING'
      }
      const setup = await beforeEachSetup(wrapper, sandbox, Account.PREMIUM, orgPaymentDetails)
      wrapper = setup.wrapper
      sandbox = setup.sandbox

      await Vue.nextTick()

      expect(wrapper.vm.hasObCredit).toBe(true)
      expect(wrapper.vm.hasPadCredit).toBe(false)
    })

    it('should calculate hasPadCredit correctly', async () => {
      const orgPaymentDetails = {
        accountId: 123,
        obCredit: '0',
        padCredit: '100.00',
        paymentMethod: 'PAD'
      }
      const setup = await beforeEachSetup(wrapper, sandbox, Account.PREMIUM, orgPaymentDetails)
      wrapper = setup.wrapper
      sandbox = setup.sandbox

      await Vue.nextTick()

      expect(wrapper.vm.hasObCredit).toBe(false)
      expect(wrapper.vm.hasPadCredit).toBe(true)
    })

    it('should calculate both credits correctly', async () => {
      const orgPaymentDetails = {
        accountId: 123,
        obCredit: '50.00',
        padCredit: '75.00',
        paymentMethod: 'ONLINE_BANKING'
      }
      const setup = await beforeEachSetup(wrapper, sandbox, Account.PREMIUM, orgPaymentDetails)
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
      const orgPaymentDetails = {
        accountId: 123,
        obCredit: '50.00',
        padCredit: '25.00',
        paymentMethod: 'ONLINE_BANKING'
      }
      const setup = await beforeEachSetup(wrapper, sandbox, Account.PREMIUM, orgPaymentDetails)
      wrapper = setup.wrapper
      sandbox = setup.sandbox

      wrapper.setProps({ showCredit: false })
      await Vue.nextTick()

      expect(wrapper.find('.credit-header-row').exists()).toBe(false)
      expect(wrapper.text()).not.toContain('Account Credit Available:')
    })

    it('should show credit section when showCredit is true and credits are available', async () => {
      const orgPaymentDetails = {
        accountId: 123,
        obCredit: '50.00',
        padCredit: '25.00',
        paymentMethod: 'ONLINE_BANKING'
      }
      const setup = await beforeEachSetup(wrapper, sandbox, Account.PREMIUM, orgPaymentDetails)
      wrapper = setup.wrapper
      sandbox = setup.sandbox

      wrapper.setProps({ showCredit: true })
      await Vue.nextTick()

      expect(wrapper.find('.credit-header-row').exists()).toBe(true)
      expect(wrapper.text()).toContain('Account Credit Available:')
    })
  })
})
