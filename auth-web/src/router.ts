import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import PaymentForm from './components/pay/PaymentForm.vue'
import PaymentReturnForm from './components/pay/PaymentReturnForm.vue'
import PageNotFound from './views/PageNotFound.vue'

Vue.use(Router)

function mapReturnPayVars (route) {
  return {
    paymentId: route.params.paymentId,
    transactionId: route.params.transactionId,
    receiptNum: !route.query.receipt_number ? '' : route.query.receipt_number
  }
}

const routes = [
  { path: '/', component: Home },
  { path: '/makepayment/:paymentId/:redirectUrl', component: PaymentForm, props: true },
  { path: '/returnpayment/:paymentId/transaction/:transactionId', component: PaymentReturnForm, props: mapReturnPayVars },
  { path: '*', component: PageNotFound }
]

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})
