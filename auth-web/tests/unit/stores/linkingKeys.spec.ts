import { createPinia, setActivePinia } from 'pinia'
import LinkingKeysService from '@/services/linkingKeys.services'
import { useLinkingKeysStore } from '@/stores/linkingKeys'

describe('linkingKeys store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
  })

  it('fetchLinkingKeys returns linking keys from API response', async () => {
    vi.spyOn(LinkingKeysService, 'getOrgLinkingKeys').mockResolvedValue({
      data: {
        linkingKeys: [{
          id: 1,
          accountId: 10,
          vendorAccountName: 'ABC API Service',
          createdOn: '2026-01-15T11:20:00Z',
          createdBy: 'William Smith',
          expiresOn: '2027-01-15T00:00:00Z'
        }]
      }
    } as any)

    const store = useLinkingKeysStore()
    const response = await store.fetchLinkingKeys(10)

    expect(LinkingKeysService.getOrgLinkingKeys).toHaveBeenCalledWith(10)
    expect(response.linkingKeys).toHaveLength(1)
    expect(response.linkingKeys[0].vendorAccountName).toBe('ABC API Service')
  })

  it('createLinkingKey calls LinkingKeysService with the create request and returns its data', async () => {
    const createSpy = vi.spyOn(LinkingKeysService, 'createOrgLinkingKey').mockResolvedValue({
      data: {
        id: 1,
        accountId: 10,
        vendorAccountId: 20,
        linkingKey: 'the-key-value',
        expiresOn: '2027-01-15T00:00:00Z',
        createdOn: '2026-01-15T11:20:00Z',
        status: 'ACTIVE'
      }
    } as any)

    const store = useLinkingKeysStore()
    const request = { orgId: 10, vendorAccountId: 20, returnUrl: 'https://vendor.example.com/callback' }
    const response = await store.createLinkingKey(request)

    expect(createSpy).toHaveBeenCalledWith(request)
    expect(response.linkingKey).toBe('the-key-value')
    expect(response.status).toBe('ACTIVE')
  })

  it('createLinkingKey propagates rejection so callers can read the error response', async () => {
    const error = { response: { status: 400, data: { code: 'REDIRECT_URL_INVALID', message: 'not allowed' } } }
    vi.spyOn(LinkingKeysService, 'createOrgLinkingKey').mockRejectedValue(error)

    const store = useLinkingKeysStore()
    await expect(store.createLinkingKey({ orgId: 10, vendorAccountId: 20, returnUrl: 'https://bad.example.com' }))
      .rejects.toBe(error)
  })

  it('revokeLinkingKey calls LinkingKeysService with linking key details', async () => {
    const revokeSpy = vi.spyOn(LinkingKeysService, 'revokeOrgLinkingKey').mockResolvedValue({ data: {} } as any)

    const store = useLinkingKeysStore()
    await store.revokeLinkingKey({ orgId: 10, keyId: 1 })

    expect(revokeSpy).toHaveBeenCalledWith({ orgId: 10, keyId: 1 })
  })

  it('extendLinkingKey calls LinkingKeysService with linking key details', async () => {
    const extendSpy = vi.spyOn(LinkingKeysService, 'extendOrgLinkingKey').mockResolvedValue({
      data: {
        id: 1,
        accountId: 10,
        expiresOn: '2028-01-15T00:00:00Z'
      }
    } as any)

    const store = useLinkingKeysStore()
    const response = await store.extendLinkingKey({ orgId: 10, keyId: 1 })

    expect(extendSpy).toHaveBeenCalledWith({ orgId: 10, keyId: 1 })
    expect(response.expiresOn).toBe('2028-01-15T00:00:00Z')
  })

  it('$reset is a no-op', () => {
    const store = useLinkingKeysStore()
    expect(() => store.$reset()).not.toThrow()
  })
})
