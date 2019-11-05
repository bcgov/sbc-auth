import Axios, { AxiosResponse } from 'axios'
import ConfigHelper from '../util/config-helper'

export default {

  createTransaction (paymentId: String, redirectUrl: String) {
    var url = `${ConfigHelper.getValue('VUE_APP_PAY_ROOT_API')}/payment-requests/${paymentId}/transactions`
    return Axios.post(url, {
      clientSystemUrl: redirectUrl,
      payReturnUrl: ConfigHelper.getSelfURL() + '/returnpayment'
    })
  },

  updateTransaction (paymentId: String, transactionId: String, receiptNum?: String) {
    const url = `${ConfigHelper.getValue('VUE_APP_PAY_ROOT_API')}/payment-requests/${paymentId}/transactions/${transactionId}?receipt_number=${receiptNum}`
    return Axios.patch(url)
  }
}
