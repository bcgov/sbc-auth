export enum NRStatus {
  NE = 'Not Examined',
  R = 'Rejected',
  A = 'Accepted',
  C = 'Cond. Accepted'

}
export interface NameRequestIF {
  name: string,
  status: string
}
export interface NameRequestLookupResultIF {
  names: NameRequestIF[]
  nrNum: string
  disabled?: boolean // for display in v-autocomplete
}

export enum LookupType {
  NR = 'nameRequest',
  BUSINESS = 'business'
}
