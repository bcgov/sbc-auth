import Axios, { AxiosResponse } from 'axios'
import { TermsOfUseDocument } from '@/models/TermsOfUseDocument'
import configHelper from '@/util/config-helper'

export default class DocumentService {
  static async getTermsOfService (identifier: string): Promise<AxiosResponse<TermsOfUseDocument>> {
    return Axios.get(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/documents/termsofuse`)
  }
}
