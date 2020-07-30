export interface Address {
  city?: string
  country?: string
  street?: string
  streetAdditional?: string
  postalCode?: string
  region?: string
  deliveryInstructions?: string
  key?: string
}

export interface BaseAddressModel {
  addressCity: string
  addressCountry: string
  addressRegion: string
  deliveryInstructions?: string
  postalCode: string
  streetAddress: string
  streetAddressAdditional?: string
}
