import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import { Transactions } from '@/components/auth/account-settings/transaction'
import Vue from 'vue'
import Vuetify from 'vuetify'
import { axios } from '@/util/http-util'
import flushPromises from 'flush-promises'
import sinon from 'sinon'
import { useOrgStore } from '@/stores/org'

export interface TestSetup {
  wrapper: Wrapper<any>
  vuetify: any
  localVue: any
}

export const createTestSetup = (): TestSetup => {
  const localVue = createLocalVue()
  const vuetify = new Vuetify({})

  return {
    wrapper: null as any,
    vuetify,
    localVue
  }
}

// Common test data factories
export const createPaymentCardData = (overrides: any = {}) => ({
  totalBalanceDue: 100,
  payeeName: 'BC Reg',
  cfsAccountId: '123456',
  obCredit: 0,
  padCredit: 0,
  paymentId: 1,
  totalPaid: 0,
  ...overrides
})

export const createOnlineBankingData = (overrides: any = {}) => ({
  totalBalanceDue: 100,
  payeeName: 'BC Reg',
  cfsAccountId: '123456',
  overCredit: false,
  partialCredit: false,
  creditBalance: 0,
  obCredit: 0,
  ...overrides
})

export const createOrgPaymentDetails = (overrides: any = {}) => ({
  accountId: 123,
  obCredit: '0',
  padCredit: '0',
  paymentMethod: 'CC',
  ...overrides
})

// Common wrapper creation functions
export const createWrapper = (
  component: any,
  propsData: any = {},
  options: any = {}
) => {
  const { localVue, vuetify } = createTestSetup()
  const $t = () => ''

  return mount(component, {
    propsData,
    localVue,
    vuetify,
    mocks: { $t },
    ...options
  })
}

// Common test helpers
export const waitForNextTick = async (wrapper: Wrapper<any>) => {
  await wrapper.vm.$nextTick()
}

export const waitForVueNextTick = async () => {
  await Vue.nextTick()
}

// Common assertions
export const expectVueInstance = (wrapper: Wrapper<any>) => {
  expect(wrapper.vm).toBeTruthy()
}

export const expectElementExists = (wrapper: Wrapper<any>, selector: string) => {
  expect(wrapper.find(selector).exists()).toBe(true)
}

export const expectElementNotExists = (wrapper: Wrapper<any>, selector: string) => {
  expect(wrapper.find(selector).exists()).toBe(false)
}

export const expectTextContains = (wrapper: Wrapper<any>, text: string) => {
  expect(wrapper.text()).toContain(text)
}

export const expectTextNotContains = (wrapper: Wrapper<any>, text: string) => {
  expect(wrapper.text()).not.toContain(text)
}

export const mountTransactionsWithStore = async (
  orgPaymentDetails: any,
  accountType: any,
  transactionResponse: any
) => {
  const { localVue, vuetify } = createTestSetup()
  const orgStore = useOrgStore()
  orgStore.currentOrgPaymentDetails = orgPaymentDetails as any
  orgStore.currentOrganization = { id: 123, orgType: accountType } as any
  orgStore.getOrgPayments = vi.fn(() => Promise.resolve(orgPaymentDetails)) as any
  orgStore.currentMembership = { membershipTypeCode: 'ADMIN' } as any
  orgStore.permissions = ['TRANSACTION_HISTORY']

  // stub axios
  const sandbox = sinon.createSandbox()
  const postStub = sandbox.stub(axios, 'post')
  postStub.returns(Promise.resolve({ data: transactionResponse }))

  const wrapper = mount(Transactions, {
    localVue,
    vuetify
  })
  await flushPromises()
  return { wrapper, sandbox }
}

export const restoreSandbox = (sandbox: any) => {
  if (sandbox) sandbox.restore()
}
