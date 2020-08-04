import { maxLength, required } from 'vuelidate/lib/validators'

// The Address schema containing Vuelidate rules.
export const addressSchema = {
  streetAddress: {
    required,
    maxLength: maxLength(50)
  },
  streetAddressAdditional: {
    maxLength: maxLength(50)
  },
  addressCity: {
    required,
    maxLength: maxLength(40)
  },
  addressCountry: {
    required
  },
  addressRegion: {
    maxLength: maxLength(2)
  },
  postalCode: {
    required,
    maxLength: maxLength(15)
  },
  deliveryInstructions: {
    maxLength: maxLength(80)
  }
}
