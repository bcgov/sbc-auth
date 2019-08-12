import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import paymentService from '@/services/payment.services'
import { PaySystemStatus } from '@/models/PaySystemStatus'
import { AxiosResponse } from 'axios'

@Module({
  name: 'paymentmodule'
})
export default class PaymentModule extends VuexModule {
    paySystemStatus: PaySystemStatus = {
      current_status: true,
      next_schedule_date: null,
      next_schedule_time: null

    }

    @Mutation
    public setPaySystemStatus (paySystemStatus: PaySystemStatus) {
      this.paySystemStatus = paySystemStatus
    }

    @Action({ commit: 'setPaySystemStatus' })
    public async fetchPaySystemStatus () {
      const response: AxiosResponse<PaySystemStatus> = await paymentService.getPaySystemStatus()
      return response.data
    }
}
