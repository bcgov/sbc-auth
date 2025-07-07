import { createLocalVue, mount } from '@vue/test-utils'
import PayWithOnlineBanking from '@/components/pay/PayWithOnlineBanking.vue'
import Vuetify from 'vuetify'

describe('PayWithOnlineBanking.vue', () => {
  let wrapper: any
  let vuetify: any
  let localVue: any

  beforeEach(() => {
    localVue = createLocalVue()
    vuetify = new Vuetify({})
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })

  const createWrapper = (onlineBankingData: any) => {
    const $t = () => ''
    return mount(PayWithOnlineBanking, {
      propsData: {
        onlineBankingData
      },
      localVue,
      vuetify,
      mocks: { $t }
    })
  }

  describe('totalBalanceDue', () => {
    it('should display totalBalanceDue correctly', async () => {
      const onlineBankingData = {
        totalBalanceDue: 150.75,
        payeeName: 'BC Reg',
        cfsAccountId: '123456',
        overCredit: false,
        partialCredit: false,
        creditBalance: 0,
        obCredit: 0
      }
      wrapper = createWrapper(onlineBankingData)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.totalBalanceDue).toBe(150.75)
      expect(wrapper.text()).toContain('$150.75')
    })

    it('should display zero balance due', async () => {
      const onlineBankingData = {
        totalBalanceDue: 0,
        payeeName: 'BC Reg',
        cfsAccountId: '123456',
        overCredit: true,
        partialCredit: false,
        creditBalance: 50,
        obCredit: 50
      }
      wrapper = createWrapper(onlineBankingData)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.totalBalanceDue).toBe(0)
      expect(wrapper.text()).toContain('$0.00')
    })

    it('should display decimal balance due', async () => {
      const onlineBankingData = {
        totalBalanceDue: 99.99,
        payeeName: 'BC Reg',
        cfsAccountId: '123456',
        overCredit: false,
        partialCredit: false,
        creditBalance: 0,
        obCredit: 0
      }
      wrapper = createWrapper(onlineBankingData)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.totalBalanceDue).toBe(99.99)
      expect(wrapper.text()).toContain('$99.99')
    })
  })

  describe('overCredit', () => {
    it('should display over credit message when overCredit is true', async () => {
      const onlineBankingData = {
        totalBalanceDue: 0,
        payeeName: 'BC Reg',
        cfsAccountId: '123456',
        overCredit: true,
        partialCredit: false,
        creditBalance: 25.50,
        obCredit: 75.50
      }
      wrapper = createWrapper(onlineBankingData)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.overCredit).toBe(true)
      expect(wrapper.text()).toContain('Transaction will be completed with your account credit')
      expect(wrapper.text()).toContain('$25.50 remaining credit')
    })

    it('should hide payee information when overCredit is true', async () => {
      const onlineBankingData = {
        totalBalanceDue: 0,
        payeeName: 'BC Reg',
        cfsAccountId: '123456',
        overCredit: true,
        partialCredit: false,
        creditBalance: 25,
        obCredit: 75
      }
      wrapper = createWrapper(onlineBankingData)
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).not.toContain('Payee Name:')
      expect(wrapper.text()).not.toContain('Payment Identifier:')
    })

    it('should hide payment instructions when overCredit is true', async () => {
      const onlineBankingData = {
        totalBalanceDue: 0,
        payeeName: 'BC Reg',
        cfsAccountId: '123456',
        overCredit: true,
        partialCredit: false,
        creditBalance: 25,
        obCredit: 75
      }
      wrapper = createWrapper(onlineBankingData)
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).not.toContain('How to pay with online banking:')
      expect(wrapper.text()).not.toContain('Sign in to your financial institution')
    })
  })

  describe('partialCredit', () => {
    it('should display partial credit message when partialCredit is true', async () => {
      const onlineBankingData = {
        totalBalanceDue: 70,
        payeeName: 'BC Reg',
        cfsAccountId: '123456',
        overCredit: false,
        partialCredit: true,
        creditBalance: 0,
        obCredit: 30
      }
      wrapper = createWrapper(onlineBankingData)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.partialCredit).toBe(true)
      expect(wrapper.text()).toContain('Payment is partially covered with your account credit: $30')
      expect(wrapper.text()).toContain('$0.00 remaining credit')
    })

    it('should show payee information when partialCredit is true', async () => {
      const onlineBankingData = {
        totalBalanceDue: 70,
        payeeName: 'BC Reg',
        cfsAccountId: '123456',
        overCredit: false,
        partialCredit: true,
        creditBalance: 0,
        obCredit: 30
      }
      wrapper = createWrapper(onlineBankingData)
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Payee Name:')
      expect(wrapper.text()).toContain('Payment Identifier:')
    })

    it('should show payment instructions when partialCredit is true', async () => {
      const onlineBankingData = {
        totalBalanceDue: 70,
        payeeName: 'BC Reg',
        cfsAccountId: '123456',
        overCredit: false,
        partialCredit: true,
        creditBalance: 0,
        obCredit: 30
      }
      wrapper = createWrapper(onlineBankingData)
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('How to pay with online banking:')
      expect(wrapper.text()).toContain('Sign in to your financial institution')
    })
  })

  describe('not over credit not partial credit', () => {
    it('should display standard message when not over credit and not partial credit', async () => {
      const onlineBankingData = {
        totalBalanceDue: 100,
        payeeName: 'BC Reg',
        cfsAccountId: '123456',
        overCredit: false,
        partialCredit: false,
        creditBalance: 0,
        obCredit: 0
      }
      wrapper = createWrapper(onlineBankingData)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.overCredit).toBe(false)
      expect(wrapper.vm.partialCredit).toBe(false)
      expect(wrapper.text()).toContain('Transaction will be completed when payment is received in full')
      expect(wrapper.text()).toContain('2-5 days')
    })

    it('should show payee information when not over credit and not partial credit', async () => {
      const onlineBankingData = {
        totalBalanceDue: 100,
        payeeName: 'BC Reg',
        cfsAccountId: '123456',
        overCredit: false,
        partialCredit: false,
        creditBalance: 0,
        obCredit: 0
      }
      wrapper = createWrapper(onlineBankingData)
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Payee Name:')
      expect(wrapper.text()).toContain('Payment Identifier:')
    })

    it('should show payment instructions when not over credit and not partial credit', async () => {
      const onlineBankingData = {
        totalBalanceDue: 100,
        payeeName: 'BC Reg',
        cfsAccountId: '123456',
        overCredit: false,
        partialCredit: false,
        creditBalance: 0,
        obCredit: 0
      }
      wrapper = createWrapper(onlineBankingData)
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('How to pay with online banking:')
      expect(wrapper.text()).toContain('Sign in to your financial institution')
      expect(wrapper.text()).toContain('Enter "BC Registries" as payee')
    })
  })

  describe('payeeName', () => {
    it('should display payeeName correctly', async () => {
      const onlineBankingData = {
        totalBalanceDue: 100,
        payeeName: 'BC Registries',
        cfsAccountId: '123456',
        overCredit: false,
        partialCredit: false,
        creditBalance: 0,
        obCredit: 0
      }
      wrapper = createWrapper(onlineBankingData)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.payeeName).toBe('BC Registries')
      expect(wrapper.text()).toContain('BC Registries')
    })

    it('should display payeeName with special characters', async () => {
      const onlineBankingData = {
        totalBalanceDue: 100,
        payeeName: 'BC Reg & Co.',
        cfsAccountId: '123456',
        overCredit: false,
        partialCredit: false,
        creditBalance: 0,
        obCredit: 0
      }
      wrapper = createWrapper(onlineBankingData)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.payeeName).toBe('BC Reg & Co.')
      expect(wrapper.text()).toContain('BC Reg & Co.')
    })

    it('should not display payeeName when overCredit is true', async () => {
      const onlineBankingData = {
        totalBalanceDue: 0,
        payeeName: 'BC Registries',
        cfsAccountId: '123456',
        overCredit: true,
        partialCredit: false,
        creditBalance: 50,
        obCredit: 50
      }
      wrapper = createWrapper(onlineBankingData)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.payeeName).toBe('BC Registries')
      expect(wrapper.text()).not.toContain('BC Registries')
    })
  })

  describe('cfsAccountId', () => {
    it('should display cfsAccountId correctly', async () => {
      const onlineBankingData = {
        totalBalanceDue: 100,
        payeeName: 'BC Reg',
        cfsAccountId: 'ABC123456',
        overCredit: false,
        partialCredit: false,
        creditBalance: 0,
        obCredit: 0
      }
      wrapper = createWrapper(onlineBankingData)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.cfsAccountId).toBe('ABC123456')
      expect(wrapper.text()).toContain('ABC123456')
    })

    it('should display cfsAccountId in payment instructions', async () => {
      const onlineBankingData = {
        totalBalanceDue: 100,
        payeeName: 'BC Reg',
        cfsAccountId: 'XYZ789012',
        overCredit: false,
        partialCredit: false,
        creditBalance: 0,
        obCredit: 0
      }
      wrapper = createWrapper(onlineBankingData)
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Enter this payment identifier as your account number: XYZ789012')
    })

    it('should not display cfsAccountId when overCredit is true', async () => {
      const onlineBankingData = {
        totalBalanceDue: 0,
        payeeName: 'BC Reg',
        cfsAccountId: 'ABC123456',
        overCredit: true,
        partialCredit: false,
        creditBalance: 50,
        obCredit: 50
      }
      wrapper = createWrapper(onlineBankingData)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.cfsAccountId).toBe('ABC123456')
      expect(wrapper.text()).not.toContain('ABC123456')
    })

    it('should handle numeric cfsAccountId', async () => {
      const onlineBankingData = {
        totalBalanceDue: 100,
        payeeName: 'BC Reg',
        cfsAccountId: 123456789,
        overCredit: false,
        partialCredit: false,
        creditBalance: 0,
        obCredit: 0
      }
      wrapper = createWrapper(onlineBankingData)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.cfsAccountId).toBe(123456789)
      expect(wrapper.text()).toContain('123456789')
    })
  })
})
