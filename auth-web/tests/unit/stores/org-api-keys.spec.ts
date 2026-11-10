import { createPinia, setActivePinia } from 'pinia'
import OrgService from '@/services/org.services'
import { useOrgStore } from '@/stores/org'

describe('Org Store - API keys environment', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
  })

  it.each([
    ['prod', 'Production'],
    ['sandbox', 'Sandbox'],
    [undefined, '']
  ])('sets the environment %s from the API keys response', async (environment, label) => {
    vi.spyOn(OrgService, 'getOrgApiKeys').mockResolvedValue({ data: { environment } } as any)
    const orgStore = useOrgStore()
    await orgStore.getOrgApiKeys(1, true)
    expect(orgStore.apiKeysEnvironmentLabel).toBe(label)
  })

  it('keeps the last known environment when a reload has none or fails', async () => {
    const orgStore = useOrgStore()
    orgStore.apiKeysEnvironment = 'prod'
    vi.spyOn(OrgService, 'getOrgApiKeys')
      .mockResolvedValueOnce({ data: {} } as any)
      .mockRejectedValueOnce(new Error('500'))
    await orgStore.getOrgApiKeys(1, true)
    await expect(orgStore.getOrgApiKeys(1, true)).rejects.toThrow()
    expect(orgStore.apiKeysEnvironment).toBe('prod')
  })

  it('clears the environment on $reset', () => {
    const orgStore = useOrgStore()
    orgStore.apiKeysEnvironment = 'prod'
    orgStore.$reset()
    expect(orgStore.apiKeysEnvironment).toBe('')
  })
})
