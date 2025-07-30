import { createPaymentCardData, createWrapper, expectElementExists, expectVueInstance, waitForNextTick } from '../test-utils/vue-test-utils'
import PaymentCard from '@/components/pay/PaymentCard.vue'
import PaymentServices from '@/services/payment.services'

// Mock PaymentServices
vi.mock('@/services/payment.services', () => ({
  default: {
    applycredit: vi.fn()
  }
}))

describe('PaymentCard.vue', () => {
  let wrapper: any

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })

  const createPaymentCardWrapper = (paymentCardData: any, showPayWithOnlyCC = false) => {
    return createWrapper(PaymentCard, {
      paymentCardData,
      showPayWithOnlyCC
    })
  }

  describe('Basic functionality', () => {
    it('is a Vue instance', () => {
      const paymentCardData = createPaymentCardData({
        totalBalanceDue: 50,
        cfsAccountId: 1234,
        obCredit: 10,
        padCredit: 5
      })
      wrapper = createPaymentCardWrapper(paymentCardData)
      expectVueInstance(wrapper)
    })

    it('Should render Payment card div', () => {
      const paymentCardData = createPaymentCardData({
        totalBalanceDue: 50,
        cfsAccountId: 1234,
        obCredit: 10,
        padCredit: 5
      })
      wrapper = createPaymentCardWrapper(paymentCardData)
      expectElementExists(wrapper, '[data-test="div-bcol-payment-card"]')
    })
  })

  describe('obCredit functionality', () => {
    it('should handle obCredit when credit is greater than balance due', () => {
      const paymentCardData = createPaymentCardData({
        totalBalanceDue: 50,
        cfsAccountId: 1234,
        obCredit: 100,
        padCredit: 5
      })
      wrapper = createPaymentCardWrapper(paymentCardData)

      expect(wrapper.vm.totalBalanceDue).toBe(50)
      expect(wrapper.vm.totalPaid).toBe(0)
      expect(wrapper.vm.overCredit).toBe(true)
      expect(wrapper.vm.partialCredit).toBe(false)
      expect(wrapper.vm.creditBalance).toBe(50) // 100 - 50
      expect(wrapper.vm.balanceDue).toBe(0)
    })

    it('should handle obCredit when credit is less than balance due', () => {
      const paymentCardData = createPaymentCardData({
        totalBalanceDue: 100,
        cfsAccountId: 1234,
        obCredit: 30,
        padCredit: 5
      })
      wrapper = createPaymentCardWrapper(paymentCardData)

      expect(wrapper.vm.overCredit).toBe(false)
      expect(wrapper.vm.partialCredit).toBe(true)
      expect(wrapper.vm.creditBalance).toBe(0)
      expect(wrapper.vm.balanceDue).toBe(70) // 100 - 30
    })

    it('should handle obCredit when credit equals balance due', () => {
      const paymentCardData = createPaymentCardData({
        totalBalanceDue: 50,
        cfsAccountId: 1234,
        obCredit: 50,
        padCredit: 5
      })
      wrapper = createPaymentCardWrapper(paymentCardData)

      expect(wrapper.vm.overCredit).toBe(true)
      expect(wrapper.vm.partialCredit).toBe(false)
      expect(wrapper.vm.creditBalance).toBe(0)
      expect(wrapper.vm.balanceDue).toBe(0)
    })

    it('should handle zero obCredit', () => {
      const paymentCardData = createPaymentCardData({
        totalBalanceDue: 50,
        cfsAccountId: 1234,
        obCredit: 0,
        padCredit: 5
      })
      wrapper = createPaymentCardWrapper(paymentCardData)

      expect(wrapper.vm.doHaveCredit).toBe(false)
      expect(wrapper.vm.overCredit).toBe(false)
      expect(wrapper.vm.partialCredit).toBe(false)
      expect(wrapper.vm.creditBalance).toBe(0)
      expect(wrapper.vm.balanceDue).toBe(50)
    })

    it('should handle undefined obCredit', () => {
      const paymentCardData = createPaymentCardData({
        totalBalanceDue: 50,
        cfsAccountId: 1234,
        obCredit: undefined,
        padCredit: 5
      })
      wrapper = createPaymentCardWrapper(paymentCardData)

      expect(wrapper.vm.doHaveCredit).toBe(false)
      expect(wrapper.vm.overCredit).toBe(false)
      expect(wrapper.vm.partialCredit).toBe(false)
      expect(wrapper.vm.creditBalance).toBe(0)
      expect(wrapper.vm.balanceDue).toBe(50)
    })
  })

  describe('padCredit functionality', () => {
    it('should include padCredit in payment card data', () => {
      const paymentCardData = createPaymentCardData({
        totalBalanceDue: 50,
        cfsAccountId: 1234,
        obCredit: 10,
        padCredit: 25
      })
      wrapper = createPaymentCardWrapper(paymentCardData)

      expect(wrapper.vm.paymentCardData.padCredit).toBe(25)
    })

    it('should handle zero padCredit', () => {
      const paymentCardData = createPaymentCardData({
        totalBalanceDue: 50,
        cfsAccountId: 1234,
        obCredit: 10,
        padCredit: 0
      })
      wrapper = createPaymentCardWrapper(paymentCardData)

      expect(wrapper.vm.paymentCardData.padCredit).toBe(0)
    })
  })

  describe('Credit calculations with totalPaid', () => {
    it('should calculate balance due correctly when totalPaid is greater than 0', () => {
      const paymentCardData = createPaymentCardData({
        totalBalanceDue: 100,
        totalPaid: 20,
        obCredit: 30,
        padCredit: 5
      })
      wrapper = createPaymentCardWrapper(paymentCardData)

      expect(wrapper.vm.totalBalanceDue).toBe(100)
      expect(wrapper.vm.totalPaid).toBe(20)
      // Initial balanceDue = 100 - 20 = 80
      // After credit applied: 80 - 30 = 50
      expect(wrapper.vm.balanceDue).toBe(50)
      expect(wrapper.vm.overCredit).toBe(false)
      expect(wrapper.vm.partialCredit).toBe(true)
    })

    it('should apply obCredit to remaining balance after totalPaid', () => {
      const paymentCardData = createPaymentCardData({
        totalBalanceDue: 100,
        totalPaid: 10,
        obCredit: 50,
        padCredit: 5
      })
      wrapper = createPaymentCardWrapper(paymentCardData)

      expect(wrapper.vm.balanceDue).toBe(40) // (100 - 10) - 50
      expect(wrapper.vm.overCredit).toBe(false)
      expect(wrapper.vm.partialCredit).toBe(true)
    })
  })

  describe('Online banking data setup', () => {
    it('should set up online banking data correctly', () => {
      const paymentCardData = createPaymentCardData({
        totalBalanceDue: 100,
        payeeName: 'BC Reg',
        cfsAccountId: '123456',
        obCredit: 30,
        padCredit: 5
      })
      wrapper = createPaymentCardWrapper(paymentCardData)

      const onlineBankingData = wrapper.vm.onlineBankingData
      expect(onlineBankingData.totalBalanceDue).toBe(70) // 100 - 30
      expect(onlineBankingData.payeeName).toBe('BC Reg')
      expect(onlineBankingData.cfsAccountId).toBe('123456')
      expect(onlineBankingData.overCredit).toBe(false)
      expect(onlineBankingData.partialCredit).toBe(true)
      expect(onlineBankingData.creditBalance).toBe(0)
      expect(onlineBankingData.credit).toBe(30)
    })

    it('should set up online banking data for over credit scenario', () => {
      const paymentCardData = createPaymentCardData({
        totalBalanceDue: 50,
        payeeName: 'BC Reg',
        cfsAccountId: '123456',
        obCredit: 100,
        padCredit: 5
      })
      wrapper = createPaymentCardWrapper(paymentCardData)

      const onlineBankingData = wrapper.vm.onlineBankingData
      expect(onlineBankingData.totalBalanceDue).toBe(0) // 50 - 50 (capped at balance due)
      expect(onlineBankingData.overCredit).toBe(true)
      expect(onlineBankingData.partialCredit).toBe(false)
      expect(onlineBankingData.creditBalance).toBe(50) // 100 - 50
    })
  })

  describe('Credit card payment flow', () => {
    it('should show credit card option when not over credit', () => {
      const paymentCardData = createPaymentCardData({
        totalBalanceDue: 100,
        payeeName: 'BC Reg',
        cfsAccountId: '123456',
        obCredit: 30,
        padCredit: 5
      })
      wrapper = createPaymentCardWrapper(paymentCardData)

      expect(wrapper.vm.overCredit).toBe(false)
      expect(wrapper.find('.pay-with-credit-card').exists()).toBe(true)
    })

    it('should hide credit card option when over credit', async () => {
      const paymentCardData = createPaymentCardData({
        totalBalanceDue: 50,
        payeeName: 'BC Reg',
        cfsAccountId: '123456',
        obCredit: 100,
        padCredit: 5
      })
      wrapper = createPaymentCardWrapper(paymentCardData)

      await waitForNextTick(wrapper)
      expect(wrapper.vm.overCredit).toBe(true)
      expect(wrapper.find('.pay-with-credit-card').exists()).toBe(false)
    })

    it('should show partial credit warning when using credit card', () => {
      const paymentCardData = createPaymentCardData({
        totalBalanceDue: 100,
        payeeName: 'BC Reg',
        cfsAccountId: '123456',
        obCredit: 30,
        padCredit: 5
      })
      wrapper = createPaymentCardWrapper(paymentCardData)

      expect(wrapper.vm.partialCredit).toBe(true)
    })
  })

  describe('Event handling', () => {
    it('should emit complete-online-banking event', async () => {
      const paymentCardData = createPaymentCardData({
        totalBalanceDue: 100,
        payeeName: 'BC Reg',
        cfsAccountId: '123456',
        obCredit: 30,
        padCredit: 5
      })
      wrapper = createPaymentCardWrapper(paymentCardData)

      await wrapper.vm.emitBtnClick('complete-online-banking')

      expect(wrapper.emitted('complete-online-banking')).toBeTruthy()
      expect(PaymentServices.applycredit).toHaveBeenCalledWith(1)
    })

    it('should emit pay-with-credit-card and download-invoice events', async () => {
      const paymentCardData = createPaymentCardData({
        totalBalanceDue: 100,
        payeeName: 'BC Reg',
        cfsAccountId: '123456',
        obCredit: 30,
        padCredit: 5
      })
      wrapper = createPaymentCardWrapper(paymentCardData)

      await wrapper.vm.emitBtnClick('pay-with-credit-card')
      expect(wrapper.emitted('pay-with-credit-card')).toBeTruthy()
      expect(PaymentServices.applycredit).not.toHaveBeenCalled()

      await wrapper.vm.emitBtnClick('download-invoice')
      expect(wrapper.emitted('download-invoice')).toBeTruthy()
      expect(PaymentServices.applycredit).not.toHaveBeenCalled()
    })

    it('should not call applycredit when no credit available', async () => {
      const paymentCardData = createPaymentCardData({
        totalBalanceDue: 100,
        payeeName: 'BC Reg',
        cfsAccountId: '123456',
        obCredit: 0,
        padCredit: 5
      })
      wrapper = createPaymentCardWrapper(paymentCardData)

      await wrapper.vm.emitBtnClick('complete-online-banking')

      expect(wrapper.emitted('complete-online-banking')).toBeTruthy()
      expect(PaymentServices.applycredit).not.toHaveBeenCalled()
    })
  })

  describe('Cancel functionality', () => {
    it('should emit complete-online-banking when canceling with showPayWithOnlyCC', async () => {
      const paymentCardData = createPaymentCardData({
        totalBalanceDue: 100,
        payeeName: 'BC Reg',
        cfsAccountId: '123456',
        obCredit: 30,
        padCredit: 5
      })
      wrapper = createPaymentCardWrapper(paymentCardData, true) // showPayWithOnlyCC = true

      await wrapper.vm.cancel()

      expect(wrapper.emitted('complete-online-banking')).toBeTruthy()
    })

    it('should set payWithCreditCard to false when canceling without showPayWithOnlyCC', () => {
      const paymentCardData = createPaymentCardData({
        totalBalanceDue: 100,
        payeeName: 'BC Reg',
        cfsAccountId: '123456',
        obCredit: 30,
        padCredit: 5
      })
      wrapper = createPaymentCardWrapper(paymentCardData, false) // showPayWithOnlyCC = false

      wrapper.vm.payWithCreditCard = true
      wrapper.vm.cancel()

      expect(wrapper.vm.payWithCreditCard).toBe(false)
    })
  })
})
