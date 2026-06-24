import { createPinia, setActivePinia } from 'pinia'
import LinkingKeysService from '@/services/linkingKeys.services'
import { useLinkingKeysStore } from '@/stores/linkingKeys'

describe('linkingKeys store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
  })

  it('fetchLinkingKeys stores linking keys from API response', async () => {
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

    expect(response.linkingKeys).toHaveLength(1)
    expect(store.linkingKeys).toHaveLength(1)
    expect(store.linkingKeys[0].vendorAccountName).toBe('ABC API Service')
    expect(store.isLoading).toBe(false)
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

  it('$reset clears linking keys state', () => {
    const store = useLinkingKeysStore()
    store.$patch({
      linkingKeys: [{ id: 1 } as any],
      isLoading: true
    })

    store.$reset()

    expect(store.linkingKeys).toEqual([])
    expect(store.isLoading).toBe(false)
  })
})
