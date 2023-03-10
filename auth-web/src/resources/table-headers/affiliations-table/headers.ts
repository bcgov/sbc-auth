import { InvoiceStatus, PaymentTypes, Product } from '@/util/constants'
import { invoiceStatusDisplay, paymentTypeDisplay, productDisplay } from '@/resources/display-mappers'
import { BaseTableHeaderI } from '@/components/datatable/interfaces'
import CommonUtils from '@/util/common-util'

export const AffiliationTableHeaders: BaseTableHeaderI[] = [
  {
    col: 'Business Name',
    hasFilter: true,
    value: 'name',
    customFilter: {
      label: 'Name',
      type: 'text',
      value: 'name',
      clearable: true
    }
  },
  {
    col: 'Number',
    hasFilter: true,
    value: 'number',
    customFilter: {
      label: 'Number',
      type: 'text',
      value: 'number',
      clearable: true
    }
  },
  {
    col: 'Type',
    hasFilter: true,
    value: 'type',
    customFilter: {
      label: 'Type',
      type: 'select',
      value: 'type',
      clearable: true
    }
  },
  {
    col: 'Status',
    hasFilter: true,
    value: 'status',
    customFilter: {
      label: 'Status',
      type: 'select',
      value: 'status',
      clearable: true
    }
  },
  {
    col: 'Actions',
    hasFilter: true,
    value: 'action'
  }
]
