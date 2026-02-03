import { PaymentTypes } from '@/util/constants'

export const paymentTypeDisplay = {
  [PaymentTypes.BCOL]: 'BC OnLine',
  [PaymentTypes.CASH]: 'Cash',
  [PaymentTypes.CHEQUE]: 'Cheque',
  [PaymentTypes.CREDIT_CARD]: 'Credit Card',
  [PaymentTypes.DIRECT_PAY]: 'Credit Card',
  [PaymentTypes.EFT]: 'Electronic Funds Transfer',
  [PaymentTypes.EJV]: 'Electronic Journal Voucher',
  [PaymentTypes.INTERNAL]: 'Routing Slip',
  [PaymentTypes.NO_FEE]: 'No Fee',
  [PaymentTypes.ONLINE_BANKING]: 'Online Banking',
  [PaymentTypes.PAD]: 'Pre-Authorized Debit',
  [PaymentTypes.CREDIT]: 'Account Credit'
}

export const paymentTypeLabel = {
  [PaymentTypes.BCOL]: 'BC ONLINE',
  [PaymentTypes.CASH]: 'CASH',
  [PaymentTypes.CHEQUE]: 'CHEQUE',
  [PaymentTypes.CREDIT_CARD]: 'CREDIT CARD',
  [PaymentTypes.DIRECT_PAY]: 'CREDIT CARD',
  [PaymentTypes.EFT]: 'ELECTRONIC FUNDS TRANSFER',
  [PaymentTypes.EJV]: 'ELECTRONIC JOURNAL VOUCHER',
  [PaymentTypes.INTERNAL]: 'ROUTING SLIP',
  [PaymentTypes.NO_FEE]: 'NO FEE',
  [PaymentTypes.ONLINE_BANKING]: 'ONLINE BANKING',
  [PaymentTypes.PAD]: 'PRE-AUTHORIZED DEBIT',
  [PaymentTypes.CREDIT]: 'ACCOUNT CREDIT'
}

export const paymentTypeIcon = {
  [PaymentTypes.BCOL]: 'mdi-link-variant',
  [PaymentTypes.CASH]: '',
  [PaymentTypes.CHEQUE]: '',
  [PaymentTypes.CREDIT_CARD]: 'mdi-credit-card-outline',
  [PaymentTypes.DIRECT_PAY]: 'mdi-credit-card-outline',
  [PaymentTypes.EFT]: 'mdi-arrow-right-circle-outline',
  [PaymentTypes.EJV]: '',
  [PaymentTypes.INTERNAL]: '',
  [PaymentTypes.NO_FEE]: '',
  [PaymentTypes.ONLINE_BANKING]: 'mdi-currency-usd',
  [PaymentTypes.PAD]: 'mdi-bank-outline',
  [PaymentTypes.CREDIT]: 'ACCOUNT CREDIT'
}
