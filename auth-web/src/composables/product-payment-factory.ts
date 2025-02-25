import { AccessType, LDFlags, PaymentTypes, ProductStatus } from '@/util/constants'
import { useCodesStore, useOrgStore } from '@/stores'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import { computed } from '@vue/composition-api'
import { storeToRefs } from 'pinia'

export const useProductPayment = (props = null, state = null) => {
  const codesStore = useCodesStore()
  const orgStore = useOrgStore()

  const PAYMENT_METHODS = {
    [PaymentTypes.CREDIT_CARD]: {
      type: PaymentTypes.CREDIT_CARD,
      icon: 'mdi-credit-card-outline',
      title: 'Credit Card',
      subtitle: 'Pay for transactions individually with your credit card.',
      description: `You don't need to provide any credit card information with your account. Credit card information will
                    be requested when you are ready to complete a transaction.`,
      supported: true
    },
    // Only show on accounts that are EFT enabled.
    [PaymentTypes.EFT]: {
      type: PaymentTypes.EFT,
      icon: 'mdi-arrow-right-circle-outline',
      title: 'Electronic Funds Transfer',
      subtitle: 'Make payments from your bank account. Statement will be issued monthly.',
      description: ``,
      supported: true
    },
    [PaymentTypes.PAD]: {
      type: PaymentTypes.PAD,
      icon: 'mdi-bank-outline',
      title: 'Pre-authorized Debit',
      subtitle: 'Automatically debit a bank account when payments are due.',
      description: '',
      supported: true
    },
    [PaymentTypes.BCOL]: {
      type: PaymentTypes.BCOL,
      icon: 'mdi-link-variant',
      title: 'BC Online',
      subtitle: 'Use your linked BC Online account for payment.',
      description: '',
      supported: true
    },
    [PaymentTypes.ONLINE_BANKING]: {
      type: PaymentTypes.ONLINE_BANKING,
      icon: 'mdi-currency-usd',
      title: 'Online Banking',
      subtitle: 'Pay for products and services through your financial institutions website.',
      description: `
          <p><strong>Online banking is currently limited to the following institutions:</strong></p>
          <p>
            <ul>
              <li>Bank of Montreal</li>
              <li>Central 1 Credit Union</li>
              <li>Coast Capital Savings</li>
              <li>HSBC</li>
              <li>Royal Bank of Canada (RBC)</li>
              <li>Scotiabank</li>
              <li>TD Canada Trust (TD)</li>
            </ul>
          </p>
          <p>
            Once your account is created, you can use your account number to add Service BC Connect as a
            payee in your financial institution's online banking system to make payments.
          </p>
          <p class="mb-0">
            Service BC Connect <strong>must receive payment in full</strong> 
            from your financial institution prior to the release of items purchased through this service. 
            Receipt of an online banking payment generally takes 3-4 days from when you make the payment with your 
            financial institution.
          </p>`,
      supported: true
    },
    // Only for GOVM clients.
    [PaymentTypes.EJV]: {
      type: PaymentTypes.EJV,
      icon: 'mdi-currency-usd',
      title: 'Electronic Journal Voucher',
      subtitle: 'Pay for transactions using your General Ledger.',
      description: '',
      supported: true
    }
  }

  // This controls the payment methods at the product level.
  const productPaymentMethods = computed(() => {
    const ppMethods = codesStore.productPaymentMethods

    let exclusionSet = [PaymentTypes.INTERNAL, PaymentTypes.EFT, PaymentTypes.EJV]
    let inclusionSet = []

    if (orgStore.currentOrganization?.accessType === AccessType.GOVM) {
      inclusionSet = [PaymentTypes.EJV]
    } else if (orgStore.currentOrgPaymentDetails?.eftEnable) {
      exclusionSet = [PaymentTypes.INTERNAL, PaymentTypes.EJV]
    }

    if (LaunchDarklyService.getFlag(LDFlags.HideBCOLProductSettings, false) &&
        orgStore.currentOrgPaymentType !== PaymentTypes.BCOL) {
      exclusionSet.push(PaymentTypes.BCOL)
    }

    Object.keys(ppMethods).forEach((product) => {
      ppMethods[product] = ppMethods[product]?.filter((method) => {
        if (inclusionSet.length > 0) {
          return inclusionSet.includes(method as PaymentTypes)
        }
        return !exclusionSet.includes(method as PaymentTypes)
      })
    })
    return ppMethods
  })

  // These two functions control the payment method selector.
  const paymentMethodSupportedForProducts = computed(() => {
    if (!props) {
      throw Error('props is required')
    }
    const {
      currentSelectedProducts
    } = storeToRefs(useOrgStore())
    const productPaymentMethods = codesStore.productPaymentMethods
    const { productList } = storeToRefs(useOrgStore())
    const derivedProductList = props.isCreateAccount ? currentSelectedProducts.value : productList.value
      .filter(item => item.subscriptionStatus === ProductStatus.ACTIVE)
      // Remove MHR sub products.
      .filter(item => !item.parentCode)
      .map(item => item.code)
    const paymentMethodProducts = {}
    for (const [product, methods] of Object.entries(productPaymentMethods)) {
      methods.forEach(method => {
        paymentMethodProducts[method] ??= []
        paymentMethodProducts[method].push(product)
      })
    }

    const paymentMethodSupported = {}
    Object.entries(paymentMethodProducts).forEach(([key, values]) => {
      paymentMethodSupported[key] = derivedProductList.every(subscription => (values as Array<string>).includes(subscription))
    })
    // Map direct pay to credit card, they are the same thing in the UI.
    if (paymentMethodSupported[PaymentTypes.DIRECT_PAY]) {
      paymentMethodSupported[PaymentTypes.CREDIT_CARD] = paymentMethodSupported[PaymentTypes.DIRECT_PAY]
    }
    // Support all products for EJV by default, might not be supported in practice, but this is similar to PAD.
    paymentMethodSupported[PaymentTypes.EJV] = true
    return paymentMethodSupported
  })

  const filteredPaymentMethods = computed(() => {
    if (!props || !state) {
      throw Error('props + state is required')
    }
    if (!props.isEditing && !props.isCreateAccount && state.selectedPaymentMethod) {
      return [PAYMENT_METHODS[state.selectedPaymentMethod]]
    }
    const methodSupportPerProduct = paymentMethodSupportedForProducts.value
    let paymentMethods = []
    const isGovmOrg = orgStore.currentOrganization?.accessType === AccessType.GOVM
    const paymentTypes = isGovmOrg ? [PaymentTypes.EJV] : [PaymentTypes.PAD, PaymentTypes.CREDIT_CARD,
      PaymentTypes.ONLINE_BANKING, PaymentTypes.BCOL, PaymentTypes.EFT]
    paymentTypes.forEach((paymentType) => {
      if (paymentType === PaymentTypes.EFT && !orgStore.currentOrgPaymentDetails?.eftEnable) {
        return
      }
      const paymentMethod = PAYMENT_METHODS[paymentType]
      if (paymentMethod && methodSupportPerProduct) {
        paymentMethod.supported = methodSupportPerProduct[paymentType]
        if (props.isCreateAccount) {
          if (orgStore.currentSelectedProducts?.length === 0) {
            paymentMethod.supported = false
          }
        }
        paymentMethods.push(paymentMethod)
      }
    })
    if (LaunchDarklyService.getFlag(LDFlags.HideBCOLProductSettings, false) &&
        orgStore.currentOrgPaymentType !== PaymentTypes.BCOL) {
      paymentMethods = paymentMethods.filter(item => item.type !== PaymentTypes.BCOL)
    }
    return paymentMethods
  })

  const hasProductOrPaymentBackendChanges = async (orgId) => {
    const clientProducts = JSON.stringify(orgStore.productList.map(p => [p.code, p.subscriptionStatus]).sort())
    await orgStore.getOrgProducts(orgId)
    const serverProducts = JSON.stringify(orgStore.productList.map(p => [p.code, p.subscriptionStatus]).sort())
    if (clientProducts !== serverProducts) {
      return true
    }
    const clientPaymentMethod = orgStore.currentOrgPaymentType
    await orgStore.getOrgPayments(orgId)
    if (clientPaymentMethod !== orgStore.currentOrgPaymentType) {
      return true
    }
    return false
  }

  return {
    productPaymentMethods,
    filteredPaymentMethods,
    paymentMethodSupportedForProducts,
    hasProductOrPaymentBackendChanges,
    PAYMENT_METHODS
  }
}
