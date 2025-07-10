import { createOnlineBankingData, createWrapper, expectTextContains, expectTextNotContains, waitForNextTick } from '../test-utils/vue-test-utils'
import PayWithOnlineBanking from '@/components/pay/PayWithOnlineBanking.vue'

describe('PayWithOnlineBanking.vue', () => {
  let wrapper: any

  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })

  const createOnlineBankingWrapper = (onlineBankingData: any) => {
    return createWrapper(PayWithOnlineBanking, { onlineBankingData })
  }

  describe('totalBalanceDue', () => {
    it('should display totalBalanceDue correctly', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 150.75,
        originalAmount: 200.00,
        overCredit: false,
        partialCredit: false
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.totalBalanceDue).toBe(150.75)
      expect(wrapper.vm.originalAmount).toBe(200.00)
      expectTextContains(wrapper, '$150.75')
      expectTextContains(wrapper, '$200.00')
    })

    it('should display Balance Due and Transaction Amount labels', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 100.00,
        originalAmount: 150.00,
        overCredit: false,
        partialCredit: false
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expectTextContains(wrapper, 'Balance Due:')
      expectTextContains(wrapper, 'Transaction Amount:')
    })

    it('should display zero balance due', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 0,
        originalAmount: 50.00,
        overCredit: true,
        partialCredit: false,
        creditBalance: 50,
        obCredit: 50
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.totalBalanceDue).toBe(0)
      expect(wrapper.vm.originalAmount).toBe(50.00)
      expectTextContains(wrapper, '$0.00')
      expectTextContains(wrapper, '$50.00')
    })

    it('should display decimal balance due', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 99.99,
        originalAmount: 99.99,
        overCredit: false,
        partialCredit: false
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.totalBalanceDue).toBe(99.99)
      expect(wrapper.vm.originalAmount).toBe(99.99)
      expectTextContains(wrapper, '$99.99')
    })
  })

  describe('overCredit', () => {
    it('should display over credit message when overCredit is true', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 0,
        originalAmount: 75.50,
        overCredit: true,
        partialCredit: false,
        creditBalance: 25.50,
        obCredit: 75.50
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.overCredit).toBe(true)
      expect(wrapper.vm.originalAmount).toBe(75.50)
      expectTextContains(wrapper, 'Transaction will be completed with your account credit')
      expectTextContains(wrapper, '$25.50 remaining credit')
      expectTextContains(wrapper, '$75.50')
    })

    it('should hide payee information when overCredit is true', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 0,
        originalAmount: 75.00,
        overCredit: true,
        partialCredit: false,
        creditBalance: 25,
        obCredit: 75
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.originalAmount).toBe(75.00)
      expectTextNotContains(wrapper, 'Payee Name:')
      expectTextNotContains(wrapper, 'Payment Identifier:')
    })

    it('should hide payment instructions when overCredit is true', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 0,
        originalAmount: 75.00,
        overCredit: true,
        partialCredit: false,
        creditBalance: 25,
        obCredit: 75
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.originalAmount).toBe(75.00)
      expectTextNotContains(wrapper, 'How to pay with online banking:')
      expectTextNotContains(wrapper, 'Sign in to your financial institution')
    })
  })

  describe('partialCredit', () => {
    it('should display partial credit message when partialCredit is true', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 70,
        originalAmount: 100.00,
        overCredit: false,
        partialCredit: true,
        creditBalance: 0,
        obCredit: 30
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.partialCredit).toBe(true)
      expect(wrapper.vm.originalAmount).toBe(100.00)
      expectTextContains(wrapper, 'Payment is partially covered with your account credit: $30')
      expectTextContains(wrapper, '$0.00 remaining credit')
      expectTextContains(wrapper, '$100.00')
    })

    it('should show payee information when partialCredit is true', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 70,
        originalAmount: 100.00,
        overCredit: false,
        partialCredit: true,
        creditBalance: 0,
        obCredit: 30
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.originalAmount).toBe(100.00)
      expectTextContains(wrapper, 'Payee Name:')
      expectTextContains(wrapper, 'Payment Identifier:')
    })

    it('should show payment instructions when partialCredit is true', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 70,
        originalAmount: 100.00,
        overCredit: false,
        partialCredit: true,
        creditBalance: 0,
        obCredit: 30
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.originalAmount).toBe(100.00)
      expectTextContains(wrapper, 'How to pay with online banking:')
      expectTextContains(wrapper, 'Sign in to your financial institution')
    })
  })

  describe('not over credit not partial credit', () => {
    it('should display standard message when not over credit and not partial credit', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 100,
        originalAmount: 100.00,
        overCredit: false,
        partialCredit: false
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.overCredit).toBe(false)
      expect(wrapper.vm.partialCredit).toBe(false)
      expect(wrapper.vm.originalAmount).toBe(100.00)
      expectTextContains(wrapper, 'Transaction will be completed when payment is received in full')
      expectTextContains(wrapper, '2-5 days')
      expectTextContains(wrapper, '$100.00')
    })

    it('should show payee information when not over credit and not partial credit', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 100,
        originalAmount: 100.00,
        overCredit: false,
        partialCredit: false
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.originalAmount).toBe(100.00)
      expectTextContains(wrapper, 'Payee Name:')
      expectTextContains(wrapper, 'Payment Identifier:')
    })

    it('should show payment instructions when not over credit and not partial credit', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 100,
        originalAmount: 100.00,
        overCredit: false,
        partialCredit: false
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.originalAmount).toBe(100.00)
      expectTextContains(wrapper, 'How to pay with online banking:')
      expectTextContains(wrapper, 'Sign in to your financial institution')
      expectTextContains(wrapper, 'Enter "BC Registries" as payee')
    })
  })

  describe('payeeName', () => {
    it('should display payeeName correctly', async () => {
      const onlineBankingData = createOnlineBankingData({
        payeeName: 'BC Registries',
        originalAmount: 100.00,
        overCredit: false,
        partialCredit: false
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.payeeName).toBe('BC Registries')
      expect(wrapper.vm.originalAmount).toBe(100.00)
      expectTextContains(wrapper, 'BC Registries')
    })

    it('should display payeeName with special characters', async () => {
      const onlineBankingData = createOnlineBankingData({
        payeeName: 'BC Reg & Co.',
        originalAmount: 150.00,
        overCredit: false,
        partialCredit: false
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.payeeName).toBe('BC Reg & Co.')
      expect(wrapper.vm.originalAmount).toBe(150.00)
      expectTextContains(wrapper, 'BC Reg & Co.')
    })

    it('should not display payeeName when overCredit is true', async () => {
      const onlineBankingData = createOnlineBankingData({
        payeeName: 'BC Registries',
        originalAmount: 50.00,
        overCredit: true,
        partialCredit: false,
        creditBalance: 50,
        obCredit: 50
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.payeeName).toBe('BC Registries')
      expect(wrapper.vm.originalAmount).toBe(50.00)
      expectTextNotContains(wrapper, 'BC Registries')
    })
  })

  describe('cfsAccountId', () => {
    it('should display cfsAccountId correctly', async () => {
      const onlineBankingData = createOnlineBankingData({
        cfsAccountId: 'ABC123456',
        originalAmount: 100.00,
        overCredit: false,
        partialCredit: false
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.cfsAccountId).toBe('ABC123456')
      expect(wrapper.vm.originalAmount).toBe(100.00)
      expectTextContains(wrapper, 'ABC123456')
    })

    it('should display cfsAccountId in payment instructions', async () => {
      const onlineBankingData = createOnlineBankingData({
        cfsAccountId: 'XYZ789012',
        originalAmount: 200.00,
        overCredit: false,
        partialCredit: false
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.originalAmount).toBe(200.00)
      expectTextContains(wrapper, 'Enter this payment identifier as your account number: XYZ789012')
    })

    it('should not display cfsAccountId when overCredit is true', async () => {
      const onlineBankingData = createOnlineBankingData({
        cfsAccountId: 'ABC123456',
        originalAmount: 50.00,
        overCredit: true,
        partialCredit: false,
        creditBalance: 50,
        obCredit: 50
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.cfsAccountId).toBe('ABC123456')
      expect(wrapper.vm.originalAmount).toBe(50.00)
      expectTextNotContains(wrapper, 'ABC123456')
    })

    it('should handle numeric cfsAccountId', async () => {
      const onlineBankingData = createOnlineBankingData({
        cfsAccountId: 123456789,
        originalAmount: 100.00,
        overCredit: false,
        partialCredit: false
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.cfsAccountId).toBe(123456789)
      expect(wrapper.vm.originalAmount).toBe(100.00)
      expectTextContains(wrapper, '123456789')
    })
  })
})
