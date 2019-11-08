import Axios, { AxiosResponse } from 'axios'
import ConfigHelper from '../util/config-helper'
import { ServiceStatus } from '@/models/ServiceStatus'

export default {

  async getPaySystemStatus (): Promise<AxiosResponse<ServiceStatus>> {
    return Axios.get(`${ConfigHelper.getValue('VUE_APP_STATUS_ROOT_API')}/status/PAYBC`)
  }

}
