import Axios, { AxiosPromise } from 'axios'
import { TransactionFilterParams, TransactionListResponse } from '@/models/transaction'
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

  static updateTransaction (paymentId: string, transactionId: string, payResponseUrl?: string): AxiosPromise<any> {
    const url = `${ConfigHelper.getPayAPIURL()}/payment-requests/${paymentId}/transactions/${transactionId}`
    return axios.patch(url, {
      payResponseUrl: payResponseUrl
    })
  }

  static getTransactions (accountId: string, filterParams: TransactionFilterParams): AxiosPromise<TransactionListResponse> {
    let params = new URLSearchParams()
    if (filterParams.pageNumber) {
      params.append('page', filterParams.pageNumber.toString())
    }
    if (filterParams.pageLimit) {
      params.append('limit', filterParams.pageLimit.toString())
    }
    const url = `${ConfigHelper.getPayAPIURL()}/accounts/${accountId}/payments/queries`
    return axios.post(url, filterParams.filterPayload, { params })
  }

  static getTransactionReports (accountId: string, filterParams: any): AxiosPromise<any> {
    const headers = {
      'Accept': 'text/csv'
    }
    const url = `${ConfigHelper.getPayAPIURL()}/accounts/${accountId}/payments/reports`
    return axios.post(url, filterParams, { headers })
  }
}
