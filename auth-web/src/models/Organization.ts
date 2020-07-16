import { BcolAccountDetails, BcolProfile } from '@/models/bcol'
import { Address } from '@/models/address'
import { Business } from '@/models/business'
import { Invitation } from '@/models/Invitation'
import { User } from '@/models/user'

export interface CreateRequestBody {
  name: string,
  typeCode?: string
  accessType?: string
  bcOnlineCredential?:BcolProfile
  mailingAddress?:Address
}

export interface Organizations
{
  orgs : Organization[]
}

export interface Organization {
  id?: number;
  name: string;
  affiliatedEntities?: Business[];
  orgType?: string;
  members?: Member[];
  invitations?: Invitation[];
  accessType?: string;
  bcolProfile?:BcolProfile
  bcolAccountDetails?:BcolAccountDetails
  grantAccess?:boolean
  statusCode?:string
  decisionMadeBy?: string,
  contactEmail?: string,
  paymentSettings?: any
}

export interface UpdateMemberPayload {
  memberId: number
  role?: string
  status?: string
  notifyUser?:boolean
}

export interface RemoveBusinessPayload {
  orgIdentifier: number
  business: Business
}

export interface Member {
  id: number
  membershipTypeCode: MembershipType
  membershipStatus: MembershipStatus
  roleDisplayName?:string
  user: User
}

export interface Members {
  members: Member []
}

export interface ActiveUserRecord {
  username: string
  name: string
  role: string
  lastActive: string
  member: Member
}

export interface PendingUserRecord {
  email: string
  invitationSent: string
  invitationExpires?: string
  invitation: Invitation
}

export enum MembershipStatus {
  'Active' = 'ACTIVE',
  'Inactive' = 'INACTIVE',
  'Rejected' = 'REJECTED',
  'Pending' = 'PENDING_APPROVAL'
}

export enum OrgStatus {
  'Active' = 'ACTIVE',
  'Inactive' = 'INACTIVE',
  'Rejected' = 'REJECTED',
  'PendingAffidavitReview' = 'PENDING_AFFIDAVIT_REVIEW'
}

export enum MembershipType {
  'Admin' = 'ADMIN',
  'Coordinator' = 'COORDINATOR',
  'User' = 'USER'
}

export interface Permissions {
  action: string[]
}

export interface RoleInfo {
  icon: string
  name: string
  desc: string,
  displayName: string,
  displayOrder: number
}

export interface AddUserBody {
  username: string
  password: string
  selectedRole?: RoleInfo
  membershipType: string
}

export interface AddUsersToOrgBody {
    users: AddUserBody[]
    orgId: string
}

export interface BulkUsersSuccess {
  username: string
  password: string
}

export interface BulkUsersFailed {
  username: string
  error: string
}

export interface BulkUserResponse {
  httpStatus: number,
  username: string,
  created?: string,
  error?: string,
  firstname?: string,
  type?: string
}

export interface BulkUserResponseBody {
  users: BulkUserResponse[]
}

export interface OrgList {
  orgs: Organization[]
  limit: number
  page: number
  total: number
}

export interface OrgFilterParams {
  status: string
  name?: string
  pageNumber?: number
  pageLimit?: number
}
