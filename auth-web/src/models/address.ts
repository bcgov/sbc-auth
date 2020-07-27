export interface Address {
  city?: string
  country?: string
  street?: string
  streetAdditional?: string
  postalCode?: string
  region?: string
  key?: string
}

export interface IAddress {
  addressCity: string
  addressCountry: string
  addressRegion: string
  deliveryInstructions?: string
  postalCode: string
  streetAddress: string
  streetAddressAdditional?: string
}
