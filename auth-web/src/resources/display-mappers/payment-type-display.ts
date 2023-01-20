import { PaymentTypes } from '@/util/constants'

export const paymentTypeDisplay = {
  [PaymentTypes.BCOL]: 'BC OnLine',
  [PaymentTypes.CASH]: 'Cash',
  [PaymentTypes.CHEQUE]: 'Cheque',
  [PaymentTypes.CREDIT_CARD]: 'Credit Card',
  [PaymentTypes.DIRECT_PAY]: 'Direct Pay',
  [PaymentTypes.EFT]: 'Electronic Funds Transfer',
  [PaymentTypes.EJV]: 'Equity Joint Venture',
  [PaymentTypes.INTERNAL]: 'Internal',
  [PaymentTypes.ONLINE_BANKING]: 'Online Banking',
  [PaymentTypes.PAD]: 'Pre-Authorized Debit',
  [PaymentTypes.WIRE]: 'Wire Transfer'
}
