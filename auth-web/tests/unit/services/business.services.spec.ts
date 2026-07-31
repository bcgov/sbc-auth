import BusinessService from '@/services/business.services'
import ConfigHelper from '@/util/config-helper'
import { axios } from '@/util/http-util'
import sinon from 'sinon'

describe('Business Services - downloadDocument', () => {
  beforeEach(() => {
    window.URL.createObjectURL = vi.fn()
    window.URL.revokeObjectURL = vi.fn()
  })

  afterEach(() => {
    sinon.restore()
    vi.restoreAllMocks()
  })

  it('downloads a DRS document via the client endpoint', async () => {
    const documentKey = 'CORP-DS0100001003'
    const url = `${ConfigHelper.getLegalAPIV2Url()}/documents/client/${documentKey}`

    const get = sinon.stub(axios, 'get').withArgs(url).returns(
      Promise.resolve({ data: new Blob(), status: 200 })
    )

    const response = await BusinessService.downloadDocument(documentKey, 'Director Affidavit.pdf')

    expect(get.calledWith(url)).toBe(true)
    expect(response.status).toBe(200)
  })

  it('downloads a legacy Minio document via the legacy endpoint', async () => {
    const documentKey = '0071dbd6-6095-46f6-b5e4-cc859b0ebf27.pdf'
    const url = `${ConfigHelper.getLegalAPIV2Url()}/documents/${documentKey}`

    const get = sinon.stub(axios, 'get').withArgs(url).returns(
      Promise.resolve({ data: new Blob(), status: 200 })
    )

    const response = await BusinessService.downloadDocument(documentKey, 'Authorization File.pdf')

    expect(get.calledWith(url)).toBe(true)
    expect(response.status).toBe(200)
  })

  it('throws on missing parameters', async () => {
    await expect(BusinessService.downloadDocument('', 'file.pdf')).rejects.toThrow('Invalid parameters')
    await expect(BusinessService.downloadDocument('some-key', '')).rejects.toThrow('Invalid parameters')
  })
})
