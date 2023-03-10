import { AffiliationTableHeaders } from './headers'
import { BaseTableHeaderI } from '@/components/datatable/interfaces'

export const getAffiliationTableHeaders = (extended = false): BaseTableHeaderI[] => {
  const headers: BaseTableHeaderI[] = []
  // values + order of headers wanted. NOTE: '' is for the actions header
  let headerTitles = []
  headerTitles = ['Business Name', 'Number', 'Type', 'Status', 'Actions']

  for (const i in headerTitles) {
    headers.push(AffiliationTableHeaders.find((header) => header.col === headerTitles[i]))
  }

  return headers
}
