import { InvoiceStatus, PaymentTypes, Product } from '@/util/constants'
import { invoiceStatusDisplay, paymentTypeDisplay, productDisplay } from '@/resources/display-mappers'
import { BaseTableHeaderI } from '@/components/datatable/interfaces'
import CommonUtils from '@/util/common-util'
import { Transaction } from '@/models/transaction'

export const TransactionTableHeaders: BaseTableHeaderI[] = [
  {
    col: 'accountName',
    customFilter: {
      clearable: true,
      label: 'Account Name',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    itemFn: (val: Transaction) => val.paymentAccount?.accountName || 'N/A',
    minWidth: '200px',
    value: 'Account Name'
  },
  {
    col: 'product',
    customFilter: {
      clearable: true,
      items: [
        { text: productDisplay[Product.BCA], value: Product.BCA },
        { text: productDisplay[Product.BUSINESS], value: Product.BUSINESS },
        { text: productDisplay[Product.BUSINESS_SEARCH], value: Product.BUSINESS_SEARCH },
        { text: productDisplay[Product.CSO], value: Product.CSO },
        { text: productDisplay[Product.ESRA], value: Product.ESRA },
        { text: productDisplay[Product.MHR], value: Product.MHR },
        { text: productDisplay[Product.PPR], value: Product.PPR },
        { text: productDisplay[Product.RPPR], value: Product.RPPR },
        { text: productDisplay[Product.RPT], value: Product.RPT },
        { text: productDisplay[Product.VS], value: Product.VS }
      ],
      label: 'Application Type',
      type: 'select',
      value: ''
    },
    hasFilter: true,
    itemFn: (val: Transaction) => (Object.keys(productDisplay)).includes(val.product) ? productDisplay[val.product] : '',
    minWidth: '200px',
    value: 'Application Type'
  },
  {
    col: 'lineItemsAndDetails',
    customFilter: {
      clearable: true,
      label: 'Transaction Type',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    itemClass: 'line-item',
    minWidth: '250px',
    value: 'Transaction Type'
  },
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
    itemFn: (val: Transaction) => val.lineItems.reduce((resp, lineItem) => `${resp + lineItem.description}<br/>`, ''),
    minWidth: '200px',
    value: 'Transaction Type'
  },
  {
    col: 'details',
    customFilter: {
      clearable: true,
      label: 'Transaction Details',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    itemFn: (val: Transaction) => val.details?.reduce((resp, detail) => `${resp}${detail.label || ''} ${detail.value}<br/>`, '') || 'N/A',
    minWidth: '200px',
    value: 'Transaction Details'
  },
  {
    col: 'businessIdentifier',
    customFilter: {
      clearable: true,
      label: 'Number',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    itemFn: (val: Transaction) => val.businessIdentifier || 'N/A',
    minWidth: '200px',
    value: 'Number'
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
    itemFn: (val: Transaction) => (val.createdName === 'None None') ? '-' : val.createdName,
    minWidth: '155px',
    value: 'Initiated by'
  },
  {
    col: 'createdOn',
    hasFilter: false,
    itemFn: (val: Transaction) => CommonUtils.formatDisplayDate(val.createdOn, 'MMMM DD, YYYY<br/>h:mm A'),
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
    col: 'invoiceNumber',
    customFilter: {
      clearable: true,
      label: 'Reference Number',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    minWidth: '250px',
    value: 'Invoice Reference Number'
  },
  {
    col: 'paymentMethod',
    customFilter: {
      clearable: true,
      items: [
        { text: paymentTypeDisplay[PaymentTypes.BCOL], value: PaymentTypes.BCOL },
        { text: paymentTypeDisplay[PaymentTypes.CREDIT_CARD], value: PaymentTypes.CREDIT_CARD },
        { text: paymentTypeDisplay[PaymentTypes.DIRECT_PAY], value: PaymentTypes.DIRECT_PAY },
        { text: paymentTypeDisplay[PaymentTypes.EJV], value: PaymentTypes.EJV },
        { text: paymentTypeDisplay[PaymentTypes.ONLINE_BANKING], value: PaymentTypes.ONLINE_BANKING },
        { text: paymentTypeDisplay[PaymentTypes.PAD], value: PaymentTypes.PAD },
        { text: paymentTypeDisplay[PaymentTypes.INTERNAL], value: PaymentTypes.INTERNAL },
        { text: paymentTypeDisplay[PaymentTypes.NO_FEE], value: PaymentTypes.NO_FEE }
      ],
      label: 'Payment Method',
      type: 'select',
      value: ''
    },
    hasFilter: true,
    itemFn: (val: Transaction) => (val.total === 0 && val.paymentMethod === PaymentTypes.INTERNAL) ? 'No Fee' : paymentTypeDisplay[val.paymentMethod],
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
        { text: invoiceStatusDisplay[InvoiceStatus.CREDITED], value: InvoiceStatus.CREDITED },
        { text: invoiceStatusDisplay[InvoiceStatus.PENDING], value: InvoiceStatus.PENDING },
        { text: invoiceStatusDisplay[InvoiceStatus.APPROVED], value: InvoiceStatus.APPROVED },
        { text: invoiceStatusDisplay[InvoiceStatus.REFUNDED], value: InvoiceStatus.REFUNDED },
        { text: invoiceStatusDisplay[InvoiceStatus.REFUND_REQUESTED], value: InvoiceStatus.REFUND_REQUESTED }
      ],
      label: 'Status',
      type: 'select',
      value: ''
    },
    itemFn: (val: Transaction) => invoiceStatusDisplay[val.statusCode],
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
