import Axios from 'axios'
import { Contact } from '../../../src/models/contact'
import { User } from '../../../src/models/user'
import UserService from '../../../src/services/user.services'

vi.mock('../../../src/services/user.services')

var mockob = {
  'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1',
  'AUTH_API_URL': 'https://auth-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
}

const mockContact : Contact = {
  email: 'test@test.com',
  phone: '555-555-5555',
  phoneExtension: '123'
}

const mockReturnUser : User = {
  firstname: 'myFirst',
  lastname: 'myLast',
  username: 'myTestUser',
  modified: new Date(),
  userTerms: {
    isTermsOfUseAccepted: true,
    termsOfUseAcceptedVersion: 'myTerm'
  }
}

const spyGetUserProfile = vi.spyOn(UserService, 'getUserProfile')
const spySyncUserProfile = vi.spyOn(UserService, 'syncUserProfile')
const spyCreateContact = vi.spyOn(UserService, 'createContact')
const spyGetContacts = vi.spyOn(UserService, 'getContacts')
const spyUpdateContact = vi.spyOn(UserService, 'updateContact')
const spyGetOrganizations = vi.spyOn(UserService, 'getOrganizations')
const spyUpdateUserTerms = vi.spyOn(UserService, 'updateUserTerms')
const spyDeactivateUser = vi.spyOn(UserService, 'deactivateUser')
const spyDeleteAnonymousUser = vi.spyOn(UserService, 'deleteAnonymousUser')
const spyGetMembership = vi.spyOn(UserService, 'getMembership')
const spyCreateUsers = vi.spyOn(UserService, 'createUsers')
const spyCreateUserProfile = vi.spyOn(UserService, 'createUserProfile')

describe('Get user profile', () => {
  const results = []
  beforeEach(() => {
    sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(mockob)
    // @ts-ignore
    vi.clearAllMocks()
  })

  it('should call get users ', () => {
    UserService.getUserProfile('@me')
    expect(spyGetUserProfile).toBeCalledTimes(1)
    expect(spyGetUserProfile).toBeCalledWith('@me')
  })

  it('should call sync user profile', () => {
    UserService.syncUserProfile()
    expect(spySyncUserProfile).toBeCalledTimes(1)
  })

  it('should call create contacts ', () => {
    UserService.createContact(mockContact)
    expect(spyCreateContact).toBeCalledTimes(1)
  })

  it('should call get contacts ', () => {
    UserService.getContacts()
    expect(spyGetContacts).toBeCalledTimes(1)
  })

  it('should call update contact ', () => {
    UserService.updateContact(mockContact)
    expect(spyUpdateContact).toBeCalledWith(mockContact)
  })

  it('should call get organization ', () => {
    UserService.getOrganizations()
    expect(spyGetOrganizations).toBeCalledTimes(1)
  })

  it('should call update user terms ', () => {
    UserService.updateUserTerms(mockReturnUser.username, mockReturnUser.userTerms.termsOfUseAcceptedVersion, mockReturnUser.userTerms.isTermsOfUseAccepted)
    expect(spyUpdateUserTerms).toBeCalledWith(mockReturnUser.username, mockReturnUser.userTerms.termsOfUseAcceptedVersion, mockReturnUser.userTerms.isTermsOfUseAccepted)
  })
})
