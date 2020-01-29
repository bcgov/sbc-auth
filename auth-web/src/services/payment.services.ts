import Axios, { AxiosPromise } from 'axios'
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

  static updateTransaction (paymentId: String, transactionId: String, receiptNum?: String): AxiosPromise<any> {
    const url = `${ConfigHelper.getPayAPIURL()}/payment-requests/${paymentId}/transactions/${transactionId}`
    return axios.patch(url, {
      receipt_number: receiptNum
    })
  }
}
