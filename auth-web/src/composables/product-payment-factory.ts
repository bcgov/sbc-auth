import { AccessType, PaymentTypes } from '@/util/constants'
import { useCodesStore, useOrgStore } from '@/stores'
import { computed } from '@vue/composition-api'

export const useProductPayment = () => {
  const codesStore = useCodesStore()
  const orgStore = useOrgStore()

  const productPaymentMethods = computed(() => {
    const ppMethods = codesStore.productPaymentMethods

    let exclusionSet = [PaymentTypes.INTERNAL, PaymentTypes.EFT, PaymentTypes.EJV]
    let inclusionSet = []

    if (orgStore.currentOrganization.accessType === AccessType.GOVM) {
      inclusionSet = [PaymentTypes.EJV]
    } else if (orgStore.currentOrgPaymentDetails?.eftEnable) {
      exclusionSet = [PaymentTypes.INTERNAL, PaymentTypes.EJV]
    }

    Object.keys(ppMethods).forEach((product) => {
      ppMethods[product] = ppMethods[product].filter((method) => {
        if (inclusionSet.length > 0) {
          return inclusionSet.includes(method as PaymentTypes)
        }
        return !exclusionSet.includes(method as PaymentTypes)
      })
    })

    return ppMethods
  })

  return {
    productPaymentMethods
  }
}
