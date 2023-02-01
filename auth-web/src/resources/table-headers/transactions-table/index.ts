import { BaseTableHeaderI } from '@/components/datatable/interfaces'
import { TransactionTableHeaders } from './headers'

export const getTransactionTableHeaders = (extended = false): BaseTableHeaderI[] => {
  const headers: BaseTableHeaderI[] = []
  // values + order of headers wanted. NOTE: '' is for the actions header
  let headerTitles = []
  if (extended) {
    headerTitles = ['accountName', 'product', 'lineItems', 'details', 'businessIdentifier', 'folioNumber',
      'createdName', 'createdOn', 'total', 'id', 'invoiceNumber', 'paymentMethod', 'statusCode', 'actions']
  } else {
    headerTitles = ['lineItemsAndDetails', 'folioNumber', 'createdName', 'createdOn',
      'total', 'id', 'paymentMethod', 'statusCode', 'actions']
  }

  for (const i in headerTitles) {
    headers.push(TransactionTableHeaders.find((header) => header.col === headerTitles[i]))
  }

  return headers
}
