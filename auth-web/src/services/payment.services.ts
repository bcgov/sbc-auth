import Axios from 'axios'
const PAYMENT_RESOURCE_NAME = '/payments'

export default {

  createTransaction (paymentId:String, redirectUrl:String) {
    const token = sessionStorage.getItem('KEYCLOAK_TOKEN')
    var url = `${process.env.VUE_APP_PAY_ROOT_API}/payments/${paymentId}/transactions?redirect_uri=${redirectUrl}`
    const config = {
      headers: { 'Authorization': `Bearer ${token}` }
    }
    return Axios.post(url, {}, config)
  },

  updateTransaction (paymentId:String, transactionId:String, receiptNum?:String) {
    const token = sessionStorage.getItem('KEYCLOAK_TOKEN')
    var url = `${process.env.VUE_APP_PAY_ROOT_API}/payments/${paymentId}/transactions/${transactionId}`
    var queryParam = receiptNum ? { receipt_number: receiptNum } : ''
    const config = {
      headers: { 'Authorization': `Bearer ${token}` }
    }
    return Axios.put(url, { params: queryParam
    }, config)
  }
}
