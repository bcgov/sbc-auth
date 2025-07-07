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
        overCredit: false,
        partialCredit: false
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.totalBalanceDue).toBe(150.75)
      expectTextContains(wrapper, '$150.75')
    })

    it('should display zero balance due', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 0,
        overCredit: true,
        partialCredit: false,
        creditBalance: 50,
        obCredit: 50
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.totalBalanceDue).toBe(0)
      expectTextContains(wrapper, '$0.00')
    })

    it('should display decimal balance due', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 99.99,
        overCredit: false,
        partialCredit: false
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.totalBalanceDue).toBe(99.99)
      expectTextContains(wrapper, '$99.99')
    })
  })

  describe('overCredit', () => {
    it('should display over credit message when overCredit is true', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 0,
        overCredit: true,
        partialCredit: false,
        creditBalance: 25.50,
        obCredit: 75.50
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.overCredit).toBe(true)
      expectTextContains(wrapper, 'Transaction will be completed with your account credit')
      expectTextContains(wrapper, '$25.50 remaining credit')
    })

    it('should hide payee information when overCredit is true', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 0,
        overCredit: true,
        partialCredit: false,
        creditBalance: 25,
        obCredit: 75
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expectTextNotContains(wrapper, 'Payee Name:')
      expectTextNotContains(wrapper, 'Payment Identifier:')
    })

    it('should hide payment instructions when overCredit is true', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 0,
        overCredit: true,
        partialCredit: false,
        creditBalance: 25,
        obCredit: 75
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expectTextNotContains(wrapper, 'How to pay with online banking:')
      expectTextNotContains(wrapper, 'Sign in to your financial institution')
    })
  })

  describe('partialCredit', () => {
    it('should display partial credit message when partialCredit is true', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 70,
        overCredit: false,
        partialCredit: true,
        creditBalance: 0,
        obCredit: 30
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.partialCredit).toBe(true)
      expectTextContains(wrapper, 'Payment is partially covered with your account credit: $30')
      expectTextContains(wrapper, '$0.00 remaining credit')
    })

    it('should show payee information when partialCredit is true', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 70,
        overCredit: false,
        partialCredit: true,
        creditBalance: 0,
        obCredit: 30
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expectTextContains(wrapper, 'Payee Name:')
      expectTextContains(wrapper, 'Payment Identifier:')
    })

    it('should show payment instructions when partialCredit is true', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 70,
        overCredit: false,
        partialCredit: true,
        creditBalance: 0,
        obCredit: 30
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expectTextContains(wrapper, 'How to pay with online banking:')
      expectTextContains(wrapper, 'Sign in to your financial institution')
    })
  })

  describe('not over credit not partial credit', () => {
    it('should display standard message when not over credit and not partial credit', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 100,
        overCredit: false,
        partialCredit: false
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.overCredit).toBe(false)
      expect(wrapper.vm.partialCredit).toBe(false)
      expectTextContains(wrapper, 'Transaction will be completed when payment is received in full')
      expectTextContains(wrapper, '2-5 days')
    })

    it('should show payee information when not over credit and not partial credit', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 100,
        overCredit: false,
        partialCredit: false
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expectTextContains(wrapper, 'Payee Name:')
      expectTextContains(wrapper, 'Payment Identifier:')
    })

    it('should show payment instructions when not over credit and not partial credit', async () => {
      const onlineBankingData = createOnlineBankingData({
        totalBalanceDue: 100,
        overCredit: false,
        partialCredit: false
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expectTextContains(wrapper, 'How to pay with online banking:')
      expectTextContains(wrapper, 'Sign in to your financial institution')
      expectTextContains(wrapper, 'Enter "BC Registries" as payee')
    })
  })

  describe('payeeName', () => {
    it('should display payeeName correctly', async () => {
      const onlineBankingData = createOnlineBankingData({
        payeeName: 'BC Registries',
        overCredit: false,
        partialCredit: false
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.payeeName).toBe('BC Registries')
      expectTextContains(wrapper, 'BC Registries')
    })

    it('should display payeeName with special characters', async () => {
      const onlineBankingData = createOnlineBankingData({
        payeeName: 'BC Reg & Co.',
        overCredit: false,
        partialCredit: false
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.payeeName).toBe('BC Reg & Co.')
      expectTextContains(wrapper, 'BC Reg & Co.')
    })

    it('should not display payeeName when overCredit is true', async () => {
      const onlineBankingData = createOnlineBankingData({
        payeeName: 'BC Registries',
        overCredit: true,
        partialCredit: false,
        creditBalance: 50,
        obCredit: 50
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.payeeName).toBe('BC Registries')
      expectTextNotContains(wrapper, 'BC Registries')
    })
  })

  describe('cfsAccountId', () => {
    it('should display cfsAccountId correctly', async () => {
      const onlineBankingData = createOnlineBankingData({
        cfsAccountId: 'ABC123456',
        overCredit: false,
        partialCredit: false
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.cfsAccountId).toBe('ABC123456')
      expectTextContains(wrapper, 'ABC123456')
    })

    it('should display cfsAccountId in payment instructions', async () => {
      const onlineBankingData = createOnlineBankingData({
        cfsAccountId: 'XYZ789012',
        overCredit: false,
        partialCredit: false
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expectTextContains(wrapper, 'Enter this payment identifier as your account number: XYZ789012')
    })

    it('should not display cfsAccountId when overCredit is true', async () => {
      const onlineBankingData = createOnlineBankingData({
        cfsAccountId: 'ABC123456',
        overCredit: true,
        partialCredit: false,
        creditBalance: 50,
        obCredit: 50
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.cfsAccountId).toBe('ABC123456')
      expectTextNotContains(wrapper, 'ABC123456')
    })

    it('should handle numeric cfsAccountId', async () => {
      const onlineBankingData = createOnlineBankingData({
        cfsAccountId: 123456789,
        overCredit: false,
        partialCredit: false
      })
      wrapper = createOnlineBankingWrapper(onlineBankingData)
      await waitForNextTick(wrapper)

      expect(wrapper.vm.cfsAccountId).toBe(123456789)
      expectTextContains(wrapper, '123456789')
    })
  })
})
