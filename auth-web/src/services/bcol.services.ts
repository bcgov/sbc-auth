import Axios, { AxiosResponse } from 'axios'
import { BcolAccountDetails, BcolProfile } from '@/models/bcol'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import { addAxiosInterceptors } from 'sbc-common-components/src/util/interceptors'

const axios = addAxiosInterceptors(Axios.create())

export default class BcolService {
  static async validateBCOL (bcOnlineProfile: BcolProfile): Promise<AxiosResponse<BcolAccountDetails>> {
    return axios.post(`${ConfigHelper.getBcolAPIURL()}/profiles`, bcOnlineProfile)
  }
}
