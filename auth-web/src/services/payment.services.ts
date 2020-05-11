import Axios, { AxiosPromise } from 'axios'
import { TransactionDateFilter, TransactionListResponse } from '@/models/transaction'
import ConfigHelper from '@/util/config-helper'
import { addAxiosInterceptors } from 'sbc-common-components/src/util/interceptors'

const axios = addAxiosInterceptors(Axios.create())

export default class PaymentService {
  static createTransaction (paymentId: string, redirectUrl: string): AxiosPromise<any> {
    var url = `${ConfigHelper.getPayAPIURL()}/payment-requests/${paymentId}/transactions`
    return axios.post(url, {
      clientSystemUrl: redirectUrl,
      payReturnUrl: ConfigHelper.getSelfURL() + '/returnpayment'
    })
  }

  static updateTransaction (paymentId: string, transactionId: string, receiptNum?: string): AxiosPromise<any> {
    const url = `${ConfigHelper.getPayAPIURL()}/payment-requests/${paymentId}/transactions/${transactionId}`
    return axios.patch(url, {
      receipt_number: receiptNum
    })
  }

  static getTransactions (accountId: string, datefilter: TransactionDateFilter): AxiosPromise<TransactionListResponse> {
    var url = `${ConfigHelper.getPayAPIURL()}/accounts/${accountId}/payments/queries`
    return axios.post(url, datefilter)
  }
}
