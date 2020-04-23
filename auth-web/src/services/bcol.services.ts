import { BcolAccountDetails, BcolProfile } from '@/models/bcol'
import { Address } from '@/models/address'
import Axios from 'axios'
import ConfigHelper from '@/util/config-helper'
import { addAxiosInterceptors } from 'sbc-common-components/src/util/interceptors'

const axios = addAxiosInterceptors(Axios.create())

export default class BcolService {
  static async validateBCOL (bcOnlineProfile: BcolProfile): Promise<BcolAccountDetails> {
    let response = await axios.post(`${ConfigHelper.getBcolAPIURL()}/profiles`, bcOnlineProfile)
    let retAddress = response.data.address

    // TODO use spread and destrcutre
    response.data.address = { region: retAddress.province,
      city: retAddress.city,
      postalCode: retAddress.postalCode,
      country: retAddress.country,
      street: retAddress.line1,
      streetAdditional: retAddress.line2 }
    return response.data
  }
}
