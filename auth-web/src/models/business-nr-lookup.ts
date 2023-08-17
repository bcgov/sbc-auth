export interface NameRequestLookupResultIF {
  names: string[]
  nrNum: string
  disabled?: boolean // for display in v-autocomplete
}

export enum LookupType {
  NR = 'nameRequest',
  BUSINESS = 'business'
}
