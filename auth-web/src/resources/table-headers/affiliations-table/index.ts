import { AffiliationTableHeaders } from './headers'
import { BaseTableHeaderI } from '@/components/datatable/interfaces'

export const getAffiliationTableHeaders = (): BaseTableHeaderI[] => {
  const headers: BaseTableHeaderI[] = []
  // values + order of headers wanted.
  let headerTitles = []
  headerTitles = ['name', 'legalType']

  for (const i in headerTitles) {
    headers.push(AffiliationTableHeaders.find((header) => header.col === headerTitles[i]))
  }

  return headers
}
