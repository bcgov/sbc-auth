import Axios from 'axios'
import ConfigHelper from '../util/config-helper'

export default {

  createTransaction (paymentId:String, redirectUrl:String) {
    var url = `${ConfigHelper.getValue('VUE_APP_PAY_ROOT_API')}/payments/${paymentId}/transactions?redirect_uri=${redirectUrl}`
    return Axios.post(url, {})
  },

  updateTransaction (paymentId:String, transactionId:String, receiptNum?:String) {
    const url = `${ConfigHelper.getValue('VUE_APP_PAY_ROOT_API')}/payments/${paymentId}/transactions/${transactionId}?receipt_number=${receiptNum}`
    return Axios.patch(url)
  }
}
