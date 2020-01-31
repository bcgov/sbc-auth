import Axios, { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { TermsOfUseDocument } from '@/models/TermsOfUseDocument'
import { addAxiosInterceptors } from 'sbc-common-components/src/util/interceptors'

const axios = addAxiosInterceptors(Axios.create())

export default class DocumentService {
  static async getTermsOfService (identifier: string): Promise<AxiosResponse<TermsOfUseDocument>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/documents/termsofuse`)
  }
}
