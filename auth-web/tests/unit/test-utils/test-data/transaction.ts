import { InvoiceStatus, PaymentTypes, Product } from '@/util/constants'
import { TransactionListResponse } from '@/models'

export const transactionResponse: TransactionListResponse = {
  items: [
    {
      businessIdentifier: '123',
      createdName: 'tester 123',
      createdOn: new Date('2023-01-24T14:00:00'),
      details: [{ label: 'label1', value: 'value1' }],
      folioNumber: 'ab12',
      id: 25663,
      invoiceNumber: 'REG000123442',
      lineItems: [{
        description: 'Statement of Registration',
        filingFees: 0,
        futureEffectiveFees: 0,
        gst: 0,
        priorityFees: 0,
        pst: 0,
        quantity: 1,
        serviceFees: 0,
        total: 0,
        waivedBy: 'tester123',
        waivedFees: 40
      }],
      paid: 0,
      paymentAccount: {
        accountId: '3040',
        accountName: "Ministry of Citizens' Services-BC Registries and Online Services Staff",
        billable: true
      },
      paymentMethod: PaymentTypes.INTERNAL,
      product: Product.PPR,
      refund: 0,
      statusCode: InvoiceStatus.COMPLETED,
      total: 0,
      updatedOn: '2023-01-24T14:00:00'
    },
    {
      businessIdentifier: '234',
      createdName: 'tester 234',
      createdOn: new Date('2023-01-23T14:00:00'),
      details: [{ label: 'label2', value: 'value2' }, { label: 'label22', value: 'value22' }],
      folioNumber: 'ab12',
      id: 25664,
      invoiceNumber: '49583jjjj',
      lineItems: [{
        description: 'Transaction description',
        filingFees: 40,
        futureEffectiveFees: 0,
        gst: 0,
        priorityFees: 0,
        pst: 0,
        quantity: 1,
        serviceFees: 0,
        total: 40,
        waivedBy: null,
        waivedFees: 0
      }],
      paid: 0,
      paymentAccount: {
        accountId: '3040',
        accountName: "Ministry of Citizens' Services-BC Registries and Online Services Staff",
        billable: true
      },
      paymentMethod: PaymentTypes.CREDIT_CARD,
      product: Product.BUSINESS,
      refund: 0,
      statusCode: InvoiceStatus.PAID,
      total: 0,
      updatedOn: '2023-01-23T14:00:00'
    }
  ],
  limit: 5,
  page: 1,
  total: 2
}
