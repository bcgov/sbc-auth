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
    value: 'Business Name',
    width: '30%'
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
    value: ' Number',
    width: '17%'
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
    value: 'Type',
    width: '25%'
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
    value: 'Status',
    width: '25%'
  },
  {
    col: 'Actions',
    hasFilter: false,
    itemClass: 'actions',
    value: 'Actions',
    width: '3%'
  }
]

export const headerTypes = {
  'Name': {
    index: 0,
    type: 'text'
  },
  'Number': {
    index: 1,
    type: 'text'
  },
  'Type': {
    index: 2,
    type: 'select'
  },
  'Status': {
    index: 3,
    type: 'select'
  },
  'Actions': {
    index: 4,
    type: ''
  }
}
