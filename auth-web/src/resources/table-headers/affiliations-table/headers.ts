import { BaseTableHeaderI } from '@/components/datatable/interfaces'
import { Business } from '@/models/business'

export const AffiliationTableHeaders: BaseTableHeaderI[] = [
  {
    col: 'name',
    customFilter: {
      clearable: true,
      label: 'Business Name',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    itemClass: 'business-name',
    value: 'Business Name'
  },
  {
    col: 'legalType',
    customFilter: {
      clearable: true,
      label: 'Legal Type',
      type: 'text',
      value: ''
    },
    hasFilter: false,
    itemFn: (val: Business) => val?.businessIdentifier || 'N/A',
    minWidth: '200px',
    value: 'Business Identifier'
  }
]
