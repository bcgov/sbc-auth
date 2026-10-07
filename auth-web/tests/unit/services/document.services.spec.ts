import ConfigHelper from '@/util/config-helper'
import DocumentService from '@/services/document.services'
import { axios } from '@/util/http-util'

describe('Document service', () => {
  let get: any
  let documentUrl: string

  beforeEach(() => {
    documentUrl = `${ConfigHelper.getAuthAPIUrl()}/documents/termsofuse_api`
    get = vi.spyOn(axios, 'get').mockResolvedValue({ data: {} })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('fetches the latest terms when no version is passed', async () => {
    await DocumentService.getTermsOfService('termsofuse_api')

    expect(get).toHaveBeenCalledWith(documentUrl, { params: undefined })
  })

  it('fetches the latest terms when an empty version is passed', async () => {
    await DocumentService.getTermsOfService('termsofuse_api', '')

    expect(get).toHaveBeenCalledWith(documentUrl, { params: undefined })
  })

  it('fetches the requested version of the terms', async () => {
    await DocumentService.getTermsOfService('termsofuse_api', '2')

    expect(get).toHaveBeenCalledWith(documentUrl, { params: { versionId: '2' } })
  })
})
