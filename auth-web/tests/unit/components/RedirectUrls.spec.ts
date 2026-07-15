import { createLocalVue, mount } from '@vue/test-utils'
import RedirectUrls from '@/components/auth/account-settings/advance-settings/RedirectUrls.vue'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

const existingUrl = {
  id: 1,
  url: 'https://example.com/existing',
  createdBy: 'Jane Doe',
  createdDate: '2027-03-22T12:00:00'
}

describe('Account settings RedirectUrls.vue', () => {
  let wrapper: any
  let orgStore: ReturnType<typeof useOrgStore>

  const $t = () => 'test trans data'

  const setExistingUrls = async (urls: any[]) => {
    await wrapper.setData({ redirectUrls: urls.map((url) => ({ ...url })) })
  }

  // Find element inside the mounted component.
  const findByTest = (id: string) => wrapper.find(`[data-test="${id}"]`)

  // Find teleported dialog/menu content outside the wrapper.
  const queryByTest = (id: string) => document.querySelector(`[data-test="${id}"]`) as HTMLElement

  const openAddForm = async () => {
    await findByTest('add-url-button').trigger('click')
  }

  const submitNewUrl = async (url?: string) => {
    await openAddForm()
    if (url !== undefined) {
      await findByTest('url-input').setValue(url)
    }
    await findByTest('confirm-add-url-button').trigger('click')
  }

  const openEditDialog = async (id: number) => {
    wrapper.vm.editUrl(id)
    await wrapper.vm.$nextTick()
  }

  beforeEach(async () => {
    const localVue = createLocalVue()

    const userStore = useUserStore()
    userStore.currentUser = { fullName: 'William Smith' } as any

    orgStore = useOrgStore()
    orgStore.currentOrganization = { id: 123, name: 'test org' } as any
    orgStore.getOrgRedirectUrls = vi.fn().mockResolvedValue({ redirectUrls: [] }) as any
    orgStore.createOrgRedirectUrl = vi.fn().mockResolvedValue({ id: 100 }) as any
    orgStore.updateOrgRedirectUrl = vi.fn().mockResolvedValue({ id: 1 }) as any
    orgStore.deleteOrgRedirectUrl = vi.fn().mockResolvedValue({}) as any

    wrapper = mount(RedirectUrls, {
      localVue,
      vuetify,
      mocks: { $t }
    })

    // Let the initial loadRedirectUrls() call settle before each test.
    await flushPromises()
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('renders the header and table headers', () => {
    expect(wrapper.find('h2').text()).toBe('Redirect URLs')
    const headers = wrapper.findAll('th').wrappers.map(th => th.text())
    expect(headers).toEqual(['Redirect URL', 'Created By', 'Created Date', 'Action'])
  })

  it('replaces the Add URL button with the inline input row on click', async () => {
    expect(findByTest('url-input').exists()).toBe(false)

    await openAddForm()

    expect(findByTest('add-url-button').exists()).toBe(false)
    expect(findByTest('add-url-helper-text').exists()).toBe(true)
    expect(findByTest('cancel-url-button').exists()).toBe(true)
    expect(findByTest('confirm-add-url-button').exists()).toBe(true)
  })

  it('restores the Add URL button on cancel and clears the input and error', async () => {
    await submitNewUrl('not a url')
    expect(wrapper.find('.v-messages__message').exists()).toBe(true)

    await findByTest('cancel-url-button').trigger('click')

    expect(findByTest('url-input').exists()).toBe(false)
    expect(findByTest('add-url-button').exists()).toBe(true)
    expect(wrapper.vm.newUrl).toBe('')
    expect(wrapper.vm.newUrlError).toBe('')
  })

  it('trims and lowercases the URL, then creates it and closes the form', async () => {
    await submitNewUrl('  HTTPS://Example.COM/Callback  ')
    await flushPromises()

    expect(orgStore.createOrgRedirectUrl).toHaveBeenCalledWith({
      orgId: 123,
      redirectUrl: 'https://example.com/callback'
    })
    expect(wrapper.vm.recentlyAddedId).toBe(100)
    expect(findByTest('url-input').exists()).toBe(false)
    expect(findByTest('add-url-button').exists()).toBe(true)
  })

  it('renders existing URLs with creator, formatted date, and no ADDED chip', async () => {
    await setExistingUrls([existingUrl])

    const rowText = wrapper.find('tbody tr').text()
    expect(rowText).toContain('Jane Doe')
    expect(rowText).toContain('Mar 22, 2027')
    expect(findByTest('url-row-0').exists()).toBe(true)
    expect(findByTest('url-added-chip-0').exists()).toBe(false)
  })

  it('calls delete after confirming the Remove dialog', async () => {
    await setExistingUrls([existingUrl])
    await findByTest('remove-url-button-0').trigger('click')

    queryByTest('confirm-remove-url-button').click()
    await flushPromises()

    expect(orgStore.deleteOrgRedirectUrl).toHaveBeenCalledWith({ orgId: 123, urlId: 1 })
  })

  it('opens the edit dialog prefilled from the dropdown menu', async () => {
    await setExistingUrls([existingUrl])
    await findByTest('more-actions-button-0').trigger('click')

    const editItem = queryByTest('edit-url-menu-item-0')
    expect(editItem.textContent).toContain('Edit URL')
    editItem.click()
    await wrapper.vm.$nextTick()

    expect((queryByTest('edit-url-input') as HTMLInputElement).value).toBe('https://example.com/existing')
  })

  it('calls update on confirm after editing', async () => {
    await setExistingUrls([existingUrl])
    await openEditDialog(existingUrl.id)

    const editInput = queryByTest('edit-url-input') as HTMLInputElement
    editInput.value = 'https://example.com/updated'
    editInput.dispatchEvent(new Event('input'))
    await wrapper.vm.$nextTick()

    queryByTest('save-edit-url-button').click()
    await flushPromises()

    expect(orgStore.updateOrgRedirectUrl).toHaveBeenCalledWith({
      orgId: 123,
      urlId: 1,
      redirectUrl: 'https://example.com/updated'
    })
    expect(wrapper.vm.editingId).toBe(null)
  })

  it('does not call update when saving an unchanged URL', async () => {
    await setExistingUrls([existingUrl])
    await openEditDialog(existingUrl.id)

    queryByTest('save-edit-url-button').click()
    await flushPromises()

    expect(orgStore.updateOrgRedirectUrl).not.toHaveBeenCalled()
    expect(wrapper.vm.editingId).toBe(null)
  })

  it('shows the duplicate error when editing a row to another existing URL', async () => {
    const otherUrl = { ...existingUrl, id: 2, url: 'https://example.com/other' }
    await setExistingUrls([existingUrl, otherUrl])
    await openEditDialog(otherUrl.id)

    const editInput = queryByTest('edit-url-input') as HTMLInputElement
    editInput.value = 'https://example.com/existing'
    editInput.dispatchEvent(new Event('input'))
    await wrapper.vm.$nextTick()

    queryByTest('save-edit-url-button').click()
    await flushPromises()

    expect(orgStore.updateOrgRedirectUrl).not.toHaveBeenCalled()
    expect(document.querySelector('.v-messages__message').textContent).toBe('This URL has already been added.')
  })

  it.each([
    ['', 'Enter a redirect URL.'],
    ['not a url', 'Enter a valid URL beginning with https://.'],
    ['example.com/callback', 'Enter a valid URL beginning with https://.'],
    ['http://example.com/callback', 'Enter a valid URL beginning with https://.']
  ])('shows an error and does not add "%s"', async (invalidUrl, message) => {
    await submitNewUrl(invalidUrl)

    expect(orgStore.createOrgRedirectUrl).not.toHaveBeenCalled()
    expect(findByTest('url-input').exists()).toBe(true)
    expect(wrapper.find('.v-messages__message').text()).toBe(message)
  })

  it.each([
    'https://example.com/callback',
    'HTTPS://EXAMPLE.COM/Callback'
  ])('shows an error and does not add a duplicate URL (%s)', async (input) => {
    await setExistingUrls([{ ...existingUrl, url: 'https://example.com/callback' }])
    await submitNewUrl(input)

    expect(orgStore.createOrgRedirectUrl).not.toHaveBeenCalled()
    expect(findByTest('url-input').exists()).toBe(true)
    expect(wrapper.find('.v-messages__message').text()).toBe('This URL has already been added.')
  })
})
