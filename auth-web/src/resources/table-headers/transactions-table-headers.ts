import { InvoiceStatus, PaymentTypes } from '@/util/constants'
import { invoiceStatusDisplay, paymentTypeDisplay } from '@/resources/display-mappers'
import { BaseTableHeaderI } from '@/components/datatable/interfaces'
import CommonUtils from '@/util/common-util'

export const TransactionTableHeaders: BaseTableHeaderI[] = [
  {
    col: 'lineItems',
    customFilter: {
      clearable: true,
      label: 'Transaction Type',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    itemClass: 'line-item',
    minWidth: '200px',
    value: 'Transaction Type'
  },
  {
    col: 'folioNumber',
    customFilter: {
      clearable: true,
      label: 'Folio #',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    minWidth: '125px',
    value: 'Folio #'
  },
  {
    col: 'createdName',
    customFilter: {
      clearable: true,
      label: 'Initiated by',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    itemFn: (val: string) => (val === 'None None') ? '-' : val,
    minWidth: '155px',
    value: 'Initiated by'
  },
  {
    col: 'createdOn',
    hasFilter: false,
    itemFn: (val: Date) => CommonUtils.formatDisplayDate(val, 'MMMM DD, YYYY<br/>h:mm A'),
    minWidth: '165px',
    value: 'Date (Pacific Time)'
  },
  {
    col: 'total',
    hasFilter: false,
    itemClass: 'font-weight-bold',
    minWidth: '135px',
    value: 'Total Amount'
  },
  {
    col: 'id',
    customFilter: {
      clearable: true,
      label: 'Transaction ID',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    minWidth: '175px',
    value: 'Transaction ID'
  },
  {
    col: 'paymentMethod',
    customFilter: {
      clearable: true,
      items: [
        { text: paymentTypeDisplay[PaymentTypes.BCOL], value: PaymentTypes.BCOL },
        { text: paymentTypeDisplay[PaymentTypes.CREDIT_CARD], value: PaymentTypes.CREDIT_CARD },
        { text: paymentTypeDisplay[PaymentTypes.DIRECT_PAY], value: PaymentTypes.DIRECT_PAY },
        { text: paymentTypeDisplay[PaymentTypes.ONLINE_BANKING], value: PaymentTypes.ONLINE_BANKING },
        { text: paymentTypeDisplay[PaymentTypes.PAD], value: PaymentTypes.PAD },
        { text: paymentTypeDisplay[PaymentTypes.INTERNAL], value: PaymentTypes.INTERNAL }
      ],
      label: 'Payment Method',
      type: 'select',
      value: ''
    },
    hasFilter: true,
    itemFn: (val: PaymentTypes) => paymentTypeDisplay[val],
    minWidth: '185px',
    value: 'Payment Method'
  },
  {
    col: 'statusCode',
    customFilter: {
      clearable: true,
      items: [
        { text: invoiceStatusDisplay[InvoiceStatus.CANCELLED], value: InvoiceStatus.CANCELLED },
        { text: invoiceStatusDisplay[InvoiceStatus.PAID], value: InvoiceStatus.PAID },
        { text: invoiceStatusDisplay[InvoiceStatus.PENDING], value: InvoiceStatus.PENDING },
        { text: invoiceStatusDisplay[InvoiceStatus.APPROVED], value: InvoiceStatus.APPROVED },
        { text: invoiceStatusDisplay[InvoiceStatus.REFUNDED], value: InvoiceStatus.REFUNDED },
        { text: invoiceStatusDisplay[InvoiceStatus.REFUND_REQUESTED], value: InvoiceStatus.REFUND_REQUESTED }
      ],
      label: 'Status',
      type: 'select',
      value: ''
    },
    itemFn: (val: InvoiceStatus) => invoiceStatusDisplay[val],
    hasFilter: true,
    minWidth: '195px',
    value: 'Payment Status'
  },
  {
    col: 'actions',
    hasFilter: false,
    minWidth: '164px',
    value: '',
    width: '164px'
  }
]
