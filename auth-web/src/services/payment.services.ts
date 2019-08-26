import Axios, { AxiosResponse } from 'axios'
import ConfigHelper from '../util/config-helper'
import { PaySystemStatus } from '@/models/PaySystemStatus'

export default {

  createTransaction (paymentId:String, redirectUrl:String) {
    var url = `${ConfigHelper.getValue('VUE_APP_PAY_ROOT_API')}/payment-requests/${paymentId}/transactions?redirect_uri=${redirectUrl}`
    return Axios.post(url, {})
  },

  updateTransaction (paymentId:String, transactionId:String, receiptNum?:String) {
    const url = `${ConfigHelper.getValue('VUE_APP_PAY_ROOT_API')}/payment-requests/${paymentId}/transactions/${transactionId}?receipt_number=${receiptNum}`
    return Axios.patch(url)
  },

  async getPaySystemStatus (): Promise<AxiosResponse<PaySystemStatus>> {
    return Axios.get(`${ConfigHelper.getValue('VUE_APP_PAY_ROOT_API')}/status/PAYBC`)
  }

}
