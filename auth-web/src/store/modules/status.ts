import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import { AxiosResponse } from 'axios'
import { ServiceStatus } from '@/models/ServiceStatus'
import StatusService from '@/services/status.services'

@Module({
  name: 'statusmodule'
})
export default class StatusModule extends VuexModule {
  paySystemStatus: ServiceStatus = {
    currentStatus: true,
    nextUpTime: null
  }

  @Mutation
  public setPaySystemStatus (serviceStatus: ServiceStatus) {
    this.paySystemStatus = serviceStatus
  }

  @Action({ commit: 'setPaySystemStatus' })
  public async fetchPaySystemStatus () {
    const response: AxiosResponse<ServiceStatus> = await StatusService.getPaySystemStatus()
    return response.data
  }
}
