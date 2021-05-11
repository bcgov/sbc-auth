import { AutoCompleteResponseIF } from '@/models/AutoComplete'
import { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { axios } from '@/util/http-util'

export default class VonService {
  public static async getAutoComplete (searchValue: string): Promise<AxiosResponse<AutoCompleteResponseIF>> {
    return axios.get(`${ConfigHelper.getVonAPIUrl()}/search/autocomplete?q=${searchValue}`)
  }
}
