import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import { AxiosResponse } from 'axios'
import { PaySystemStatus } from '@/models/PaySystemStatus'
import PaymentService from '@/services/payment.services'

@Module({
  name: 'paymentmodule'
})
export default class PaymentModule extends VuexModule {
  paySystemStatus: PaySystemStatus = {
    currentStatus: true,
    nextScheduleDate: null,
    nextScheduleTime: null
  }

  @Mutation
  public setPaySystemStatus (paySystemStatus: PaySystemStatus) {
    this.paySystemStatus = paySystemStatus
  }

  @Action({ commit: 'setPaySystemStatus' })
  public async fetchPaySystemStatus () {
    const response: AxiosResponse<PaySystemStatus> = await PaymentService.getPaySystemStatus()
    return response.data
  }
}
