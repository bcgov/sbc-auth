import { BcolAccountDetails, BcolProfile } from '@/models/bcol'
import ConfigHelper from '@/util/config-helper'
import { axios } from '@/util/http-util'

export default class BcolService {
  static async validateBCOL (bcOnlineProfile: BcolProfile): Promise<BcolAccountDetails> {
    let response = await axios.post(`${ConfigHelper.getAuthAPIUrl()}/bcol-profiles`, bcOnlineProfile)
    const retAddress = response.data.address

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
