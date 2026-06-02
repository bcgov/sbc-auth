import { createPinia, setActivePinia } from 'pinia'
import { Contact } from '@/models/contact'
import UserService from '@/services/user.services'
import { useUserStore } from '@/stores/user'

describe('User Store - contact idempotency', () => {
  const contact: Contact = {
    email: 'test@example.com',
    phone: '555-555-5555',
    phoneExtension: '123'
  }

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('createUserContact falls back to update when contact exists', async () => {
    const userStore = useUserStore()
    const createSpy = vi.spyOn(UserService, 'createContact').mockRejectedValue({
      response: { data: { code: 'DATA_ALREADY_EXISTS' } }
    })
    const updateSpy = vi.spyOn(UserService, 'updateContact').mockResolvedValue({ status: 200, data: contact } as any)

    const result = await userStore.createUserContact(contact)

    expect(createSpy).toHaveBeenCalledWith(contact)
    expect(updateSpy).toHaveBeenCalledWith(contact)
    expect(result).toEqual(contact)
    expect(userStore.userContact).toEqual(contact)
  })

  it('updateUserContact falls back to create when contact is missing', async () => {
    const userStore = useUserStore()
    const updateSpy = vi.spyOn(UserService, 'updateContact').mockRejectedValue({
      response: { data: { code: 'DATA_NOT_FOUND' } }
    })
    const createSpy = vi.spyOn(UserService, 'createContact').mockResolvedValue({ status: 201, data: contact } as any)

    const result = await userStore.updateUserContact(contact)

    expect(updateSpy).toHaveBeenCalledWith(contact)
    expect(createSpy).toHaveBeenCalledWith(contact)
    expect(result).toEqual(contact)
    expect(userStore.userContact).toEqual(contact)
  })
})
