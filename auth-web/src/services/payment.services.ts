import Axios, { AxiosPromise } from 'axios'
import { FilingTypeResponse, GLCode, GLCodeResponse } from '@/models/Staff'
import { StatementFilterParams, StatementListResponse } from '@/models/statement'
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

  static getStatementsList (accountId: string, filterParams: StatementFilterParams): AxiosPromise<StatementListResponse> {
    let params = new URLSearchParams()
    if (filterParams.pageNumber) {
      params.append('page', filterParams.pageNumber.toString())
    }
    if (filterParams.pageLimit) {
      params.append('limit', filterParams.pageLimit.toString())
    }
    const url = `${ConfigHelper.getPayAPIURL()}/accounts/${accountId}/statements`
    return axios.get(url, { params })
  }

  static getGLCodeList (): AxiosPromise<GLCodeResponse> {
    return axios.get(`${ConfigHelper.getPayAPIURL()}/fees/distributions`)
  }

  static getGLCodeFiling (distributionCodeId: string): AxiosPromise<FilingTypeResponse> {
    return axios.get(`${ConfigHelper.getPayAPIURL()}/fees/distributions/${distributionCodeId}/schedules`)
  }

  static updateGLCodeFiling (glcodeFilingData: GLCode): AxiosPromise<GLCodeResponse> {
    return axios.put(`${ConfigHelper.getPayAPIURL()}/fees/distributions/${glcodeFilingData.distributionCodeId}`, glcodeFilingData)
  }
}
