import Axios, { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { Organization } from '@/models/Organization'
import { TermsOfUseDocument } from '@/models/TermsOfUseDocument'
import { addAxiosInterceptors } from 'sbc-common-components/src/util/interceptors'

const axios = addAxiosInterceptors(Axios.create())

export default class DocumentService {
  static async getTermsOfService (identifier: string): Promise<AxiosResponse<TermsOfUseDocument>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/documents/termsofuse`)
  }
  static async getAffidavitPdf (): Promise<AxiosResponse> {
    return axios.get(`${ConfigHelper.getFileServerUrl()}/affidavit_v1.pdf`, {
      responseType: 'arraybuffer',
      headers: {
        'Accept': 'application/pdf'
      }
    })
  }

  // TODO - modify this once document upload/get for completed affidavits in place
  static async getAffidavitForOrg (org: Organization): Promise<AxiosResponse> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/${org.id}/admins/affidavits`, {
      responseType: 'arraybuffer',
      headers: {
        'Accept': 'application/pdf'
      }
    })
  }
}
