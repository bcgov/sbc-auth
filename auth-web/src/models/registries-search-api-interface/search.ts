import { ErrorI } from '.'
import { BusinessStatuses, BusinessTypes, CorpTypeCd } from '@/enums'

// api responses
export interface SearchResultI {
  name: string
  identifier: string
  bn: string
  status: BusinessStatuses.ACTIVE | BusinessStatuses.HISTORICAL
  legalType: BusinessTypes | CorpTypeCd
}
export interface SearchPartyResultI {
  parentBN: string
  parentIdentifier: string
  parentLegalType: BusinessTypes | CorpTypeCd
  parentName: string
  parentStatus: BusinessStatuses.ACTIVE | BusinessStatuses.HISTORICAL
  partyName: string
  partyRoles: string[]
  partyType: 'person' | 'organization'
}
export interface SearchResponseI {
  searchResults: {
    results: (SearchResultI | SearchPartyResultI)[]
    totalResults: number
  }
  error?: ErrorI
}
