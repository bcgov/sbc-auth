import Axios from 'axios'
const PAYMENT_RESOURCE_NAME = '/payments'

export default {
  get_paybc_url (payId) {
    const token = sessionStorage.token
    const traceid = sessionStorage.traceid

    var url = `${process.env.VUE_APP_PAY_API}${PAYMENT_RESOURCE_NAME}/paybc/${payId}`

    /* return Axios.get(url, {
      headers: {
        Authorization: `Bearer ${token}`,
        'registries-trace-id': `${traceid}`
      }
    }) */

    return Axios.get(
      `https://mock-sbc-pay.pathfinder.gov.bc.ca/rest/SBC+Pay+API+Reference/1.0.2/api/v1/payments/12345678/url`
    )
  },
  get_payment_status (payId) {
    const token = sessionStorage.token
    const traceid = sessionStorage.traceid

    var url = `${process.env.VUE_APP_PAY_API}${PAYMENT_RESOURCE_NAME}/status/${payId}`

    /* return Axios.get(url, {
      headers: {
        Authorization: `Bearer ${token}`,
        'registries-trace-id': `${traceid}`
      }
    })
  } */
    return Axios.get(`https://mock-sbc-pay.pathfinder.gov.bc.ca/rest/SBC+Pay+API+Reference/1.0.2/api/v1/12345678`)
  }
}
