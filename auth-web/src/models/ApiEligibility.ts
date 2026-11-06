export interface ApiEligibility {
  isApiEligible: boolean
  isAccountActive: boolean
  isPaymentMethodValid: boolean | null
  paymentMethod: string | null
}
