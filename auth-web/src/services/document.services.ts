import { TermsOfUseDocument } from '@/models/TermsOfUseDocument'
import { DocumentUpload } from '@/models/user'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { axios } from '@/util/http-util'
import Axios, { AxiosResponse } from 'axios'
import mime from 'mime-types'

export default class DocumentService {
  static async getTermsOfService (identifier: string): Promise<AxiosResponse<TermsOfUseDocument>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/documents/${identifier}`)
  }

  static async getAffidavitPdf (): Promise<AxiosResponse> {
    const instance = Axios.create()
    return instance.get(`${ConfigHelper.getFileServerUrl()}/affidavit_v1.pdf`, {
      responseType: 'arraybuffer',
      headers: {
        'Accept': 'application/pdf'
      }
    })
  }

  static async getSignedAffidavit (documentUrl: string, fileName: string): Promise<void> {
    const data = await axios.get(documentUrl, {
      responseType: 'arraybuffer'
    })
    const extension = mime.extension(data?.headers['content-type']) || 'file' // Default to .file if mime type is not known
    CommonUtils.fileDownload(data?.data, `${fileName}.${extension}`, data?.headers['content-type'])
  }

  static async getPresignedUrl (fileName: string): Promise<AxiosResponse<DocumentUpload>> {
    return axios.get(
      `${ConfigHelper.getAuthAPIUrl()}/documents/${fileName}/signatures`
    )
  }

  static async uplpoadToUrl (url: string, file:File, key:String, userId: string): Promise<AxiosResponse> {
    const options = {
      headers: {
        'Content-Type': file.type,
        'x-amz-meta-userid': `${userId}`,
        'x-amz-meta-key': `${key}`,
        'Content-Disposition': `attachment; filename=${file.name}`
      }
    }
    const response = await axios.put(
      url, file, options
    )
    return response
  }
}
