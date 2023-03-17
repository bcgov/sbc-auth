import { BaseTableHeaderI } from '@/components/datatable/interfaces'

export const AffiliationTableHeaders: BaseTableHeaderI[] = [
  {
    col: 'Name',
    customFilter: {
      clearable: true,
      label: 'Name',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    itemClass: 'business-name',
    value: 'Business Name'
  },
  {
    col: 'Number',
    customFilter: {
      clearable: true,
      label: 'Number',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    itemClass: 'business-number',
    value: ' Number'
  },
  {
    col: 'Type',
    customFilter: {
      clearable: true,
      label: 'Type',
      type: 'select',
      value: ''
    },
    hasFilter: true,
    itemClass: 'business-type',
    value: 'Type'
  },
  {
    col: 'Status',
    customFilter: {
      clearable: true,
      label: 'Status',
      type: 'select',
      value: ''
    },
    hasFilter: true,
    itemClass: 'business-status',
    value: 'Status'
  },
  {
    col: 'Actions',
    hasFilter: false,
    itemClass: 'actions',
    value: 'Actions'
  }
]
