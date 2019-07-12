import Axios from 'axios'
const PAYMENT_RESOURCE_NAME = '/pay/api/payments'

export default {

  createTransaction (paymentId:String, redirectUrl:String) {
    var url = `${PAYMENT_RESOURCE_NAME}/${paymentId}/transactions?redirect_uri=${redirectUrl}`
    return Axios.post(url, {})
  },

  updateTransaction (paymentId:String, transactionId:String, receiptNum?:String) {
    const token = sessionStorage.getItem('KEYCLOAK_TOKEN')
    const url = `${PAYMENT_RESOURCE_NAME}/${paymentId}/transactions/${transactionId}?receipt_number=${receiptNum}`
    return Axios.put(url)
  }
}
