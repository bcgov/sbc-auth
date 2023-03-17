import { AffiliationTableHeaders } from './headers'
import { BaseTableHeaderI } from '@/components/datatable/interfaces'

export const getAffiliationTableHeaders = (headersArray?: string[]): BaseTableHeaderI[] => {
  const headers: BaseTableHeaderI[] = []
  // values + order of headers wanted.
  let headerTitles = ['Name']
  if (headersArray) {
    headerTitles = headerTitles.concat(headersArray)
  } else {
    headerTitles = headerTitles.concat(['Number', 'Type', 'Status'])
  }
  headerTitles.push('Actions')
  for (const i in headerTitles) {
    headers.push(AffiliationTableHeaders.find((header) => header.col === headerTitles[i]))
  }

  return headers
}
