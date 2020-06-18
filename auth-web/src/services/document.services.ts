import Axios, { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { DocumentUpload } from '@/models/user'
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

  static async getPresignedUrl (fileName: string): Promise<AxiosResponse<DocumentUpload>> {
    return axios.get(
      `${ConfigHelper.getAuthAPIUrl()}/documents/${fileName}/signatures`
    )
  }

  static async uplpoadToUrl (url: string, file:File, key:String, userId: string): Promise<AxiosResponse> {
    var options = {
      headers: {
        'Content-Type': file.type,
        'x-amz-meta-userid': `${userId}`,
        'x-amz-meta-key': `${key}`,
        'Content-Disposition': `attachment; filename=${file.name}`
      }
    }
    let response = await axios.put(
      url, file, options
    )
    return response
  }
}
