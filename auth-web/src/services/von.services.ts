import { AutoCompleteResponse } from '@/models/AutoComplete'
import { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { axios } from '@/util/http-util'

export default class VonService {
  public static async getOrgNameAutoComplete (searchValue: string): Promise<AxiosResponse<AutoCompleteResponse>> {
    return axios.get(`${ConfigHelper.getVonAPIUrl()}/search/autocomplete?q=${searchValue}&inactive=false`)
  }
}
