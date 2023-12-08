import { FilingTypeResponse, GLCode, GLCodeResponse } from '@/models/Staff'
import { Invoice, InvoiceListResponse } from '@/models/invoice'
import { PADInfo, PADInfoValidation } from '@/models/Organization'
import {
  StatementFilterParams,
  StatementListItem,
  StatementListResponse,
  StatementNotificationSettings,
  StatementSettings
} from '@/models/statement'
import { TransactionFilter, TransactionFilterParams, TransactionListResponse } from '@/models/transaction'

import { AxiosPromise } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { Payment } from '@/models/Payment'
import { PaymentTypes } from '@/util/constants'
import { axios } from '@/util/http-util'

export default class PaymentService {
  static createTransaction (paymentId: string, redirectUrl: string): AxiosPromise<any> {
    const url = `${ConfigHelper.getPayAPIURL()}/payment-requests/${paymentId}/transactions`
    return axios.post(url, {
      clientSystemUrl: redirectUrl,
      payReturnUrl: ConfigHelper.getSelfURL() + '/returnpayment'
    })
  }

  static getInvoice (invoiceId: string, accountId: number): AxiosPromise<Invoice> {
    const headers = accountId ? { 'Account-Id': accountId } : {}
    return axios.get(`${ConfigHelper.getPayAPIURL()}/payment-requests/${invoiceId}`, { headers: headers })
  }

  static updateInvoicePaymentMethodAsCreditCard (paymentId: string, accountId: number): AxiosPromise<any> {
    const headers = accountId ? { 'Account-Id': accountId } : {}
    const url = `${ConfigHelper.getPayAPIURL()}/payment-requests/${paymentId}`
    return axios.patch(url, {
      paymentInfo: {
        methodOfPayment: PaymentTypes.CREDIT_CARD
      }
    }, {
      headers: headers
    }
    )
  }

  static downloadOBInvoice (paymentId: string): AxiosPromise<any> {
    const url = `${ConfigHelper.getPayAPIURL()}/payment-requests/${paymentId}/reports`
    const headers = {
      'Accept': 'application/pdf'
    }
    return axios.post(url, {}, { headers, responseType: 'blob' as 'json' })
  }

  static updateTransaction (paymentId: string, transactionId: string, payResponseUrl?: string): AxiosPromise<any> {
    const url = `${ConfigHelper.getPayAPIURL()}/payment-requests/${paymentId}/transactions/${transactionId}`
    return axios.patch(url, {
      payResponseUrl: payResponseUrl
    })
  }

  static applycredit (paymentId: string): AxiosPromise<any> {
    return axios.patch(`${ConfigHelper.getPayAPIURL()}/payment-requests/${paymentId}?applyCredit=true`, {})
  }

  static createTransactionForPadPayment (paymentId: string, redirectUrl: string): AxiosPromise<any> {
    const url = `${ConfigHelper.getPayAPIURL()}/payments/${paymentId}/transactions`
    return axios.post(url, {
      clientSystemUrl: redirectUrl,
      payReturnUrl: ConfigHelper.getSelfURL() + '/return-cc-payment'
    })
  }

  static updateTransactionForPadPayment (paymentId: string, transactionId: string, payResponseUrl?: string): AxiosPromise<any> {
    const url = `${ConfigHelper.getPayAPIURL()}/payments/${paymentId}/transactions/${transactionId}`
    return axios.patch(url, {
      payResponseUrl: payResponseUrl
    })
  }

  static getTransactions (accountId: number, filterParams: TransactionFilterParams, viewAll = false): AxiosPromise<TransactionListResponse> {
    const params = new URLSearchParams()
    if (filterParams.pageNumber) {
      params.append('page', filterParams.pageNumber.toString())
    }
    if (filterParams.pageLimit) {
      params.append('limit', filterParams.pageLimit.toString())
    }
    if (viewAll) params.append('viewAll', `${viewAll}`)

    const url = `${ConfigHelper.getPayAPIURL()}/accounts/${accountId}/payments/queries`
    return axios.post(url, filterParams.filterPayload, { params })
  }

  static getTransactionReports (accountId: number, filterParams: TransactionFilter): AxiosPromise<any> {
    const headers = {
      'Accept': 'text/csv'
    }
    const url = `${ConfigHelper.getPayAPIURL()}/accounts/${accountId}/payments/reports`
    return axios.post(url, filterParams, { headers, responseType: 'blob' as 'json' })
  }

  static getStatementsList (accountId: string | number, filterParams: StatementFilterParams): AxiosPromise<StatementListResponse> {
    const params = new URLSearchParams()
    if (filterParams.pageNumber) {
      params.append('page', filterParams.pageNumber.toString())
    }
    if (filterParams.pageLimit) {
      params.append('limit', filterParams.pageLimit.toString())
    }
    const url = `${ConfigHelper.getPayAPIURL()}/accounts/${accountId}/statements`
    return axios.get(url, { params })
  }

  static getStatementSettings (accountId: string | number): AxiosPromise<StatementSettings> {
    return axios.get(`${ConfigHelper.getPayAPIURL()}/accounts/${accountId}/statements/settings`)
  }

  static getStatementsSummary (accountId: string | number): AxiosPromise<any> {
    const url = `${ConfigHelper.getPayAPIURL()}/accounts/${accountId}/statements/summary`
    return axios.get(url)
  }

  static getStatement (accountId: string | number, statementId: string, type: string): AxiosPromise<any> {
    const headers = {
      'Accept': type
    }
    const url = `${ConfigHelper.getPayAPIURL()}/accounts/${accountId}/statements/${statementId}`
    return axios.get(url, { headers, responseType: 'blob' as 'json' })
  }

  static updateStatementSettings (accountId: string | number, updateBody): AxiosPromise<StatementListItem> {
    return axios.post(`${ConfigHelper.getPayAPIURL()}/accounts/${accountId}/statements/settings`, updateBody)
  }

  static getStatementRecipients (accountId: string | number): AxiosPromise<StatementNotificationSettings> {
    return axios.get(`${ConfigHelper.getPayAPIURL()}/accounts/${accountId}/statements/notifications`)
  }

  static updateStatementNotifications (accountId: string | number, updateBody): AxiosPromise<StatementNotificationSettings> {
    return axios.post(`${ConfigHelper.getPayAPIURL()}/accounts/${accountId}/statements/notifications`, updateBody)
  }

  static getGLCodeList (): AxiosPromise<GLCodeResponse> {
    return axios.get(`${ConfigHelper.getPayAPIURL()}/fees/distributions`)
  }

  static getGLCode (distributionCodeId: number): AxiosPromise<GLCode> {
    return axios.get(`${ConfigHelper.getPayAPIURL()}/fees/distributions/${distributionCodeId}`)
  }

  static getGLCodeFiling (distributionCodeId: number): AxiosPromise<FilingTypeResponse> {
    return axios.get(`${ConfigHelper.getPayAPIURL()}/fees/distributions/${distributionCodeId}/schedules`)
  }

  static updateGLCodeFiling (glcodeFilingData: GLCode): AxiosPromise<GLCode> {
    return axios.put(`${ConfigHelper.getPayAPIURL()}/fees/distributions/${glcodeFilingData.distributionCodeId}`, glcodeFilingData)
  }

  static verifyPADInfo (padInfo: PADInfo): AxiosPromise<PADInfoValidation> {
    return axios.post(`${ConfigHelper.getPayAPIURL()}/bank-accounts/verifications`, padInfo)
  }

  static getFailedInvoices (accountId: string | number): AxiosPromise<InvoiceListResponse> {
    return axios.get(`${ConfigHelper.getPayAPIURL()}/accounts/${accountId}/payments?status=FAILED`)
  }

  static createAccountPayment (accountId: string | number) :AxiosPromise<Payment> {
    return axios.post(`${ConfigHelper.getPayAPIURL()}/accounts/${accountId}/payments?retryFailedPayment=true`, {})
  }

  static getRevenueAccountDetails (accountId: number): AxiosPromise<any> {
    return axios.get(`${ConfigHelper.getPayAPIURL()}/accounts/${accountId}`)
  }

  static getOrgProductFeeCodes (): AxiosPromise<any> {
    return axios.get(`${ConfigHelper.getPayAPIURL()}/codes/fee_codes`)
  }

  static createAccountFees (accountId: string | number, accountFeePayload: any): AxiosPromise<any> {
    return axios.post(`${ConfigHelper.getPayAPIURL()}/accounts/${accountId}/fees`, accountFeePayload)
  }

  static getAccountFees (accountId: string | number): AxiosPromise<any> {
    return axios.get(`${ConfigHelper.getPayAPIURL()}/accounts/${accountId}`)
  }

  static updateAccountFees (accountId: string | number, accountFeePayload: any): AxiosPromise<any> {
    const { product } = accountFeePayload
    return axios.put(`${ConfigHelper.getPayAPIURL()}/accounts/${accountId}/fees/${product}`, accountFeePayload)
  }

  static removeAccountFees (accountId: string | number): AxiosPromise<any> {
    return axios.delete(`${ConfigHelper.getPayAPIURL()}/accounts/${accountId}/fees`)
  }

  static getNSFInvoices (accountId: string | number): AxiosPromise<any> {
    return axios.get(`${ConfigHelper.getPayAPIURL()}/accounts/${accountId}/nsf`)
  }

  static downloadNSFInvoicesPDF (accountId: string | number): AxiosPromise<any> {
    const url = `${ConfigHelper.getPayAPIURL()}/accounts/${accountId}/nsf/statement`
    const headers = { 'Accept': 'application/pdf' }
    const body = {}
    return axios.post(url, body, { headers, responseType: 'blob' as 'json' })
  }
}
