import { BcolAccountDetails, BcolProfile } from '@/models/bcol'

import { Address } from '@/models/address'
import { Business } from '@/models/business'
import { Invitation } from '@/models/Invitation'
import { User } from '@/models/user'

export interface CreateRequestBody {
  name?: string,
  branchName?: string
  typeCode?: string
  accessType?: string
  bcOnlineCredential?:BcolProfile
  mailingAddress?:Address
  paymentInfo?: PaymentInfo
  productSubscriptions?: []
  isBusinessAccount?: boolean
  businessType?: string
  businessSize?: string
}

export interface PaymentInfo {
  paymentMethod?: string
  bankTransitNumber?: string
  bankInstitutionNumber?: string
  bankAccountNumber?: string
  revenueAccount?: GLInfo
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
  bcolAccountName?: string,
  grantAccess?:boolean
  statusCode?:string
  decisionMadeBy?: string,
  contactEmail?: string,
  paymentSettings?: any,
  bcolAccountId?: string,
  bcolUserId?: string,
  suspendedOn?: string,
  accountStatus?: string,
  suspensionReasonCode?: string,
  branchName?: string,
  isBusinessAccount?: boolean,
  businessType?: string,
  businessSize?: string
}

export interface PADInfo {
  bankAccountNumber: string;
  bankInstitutionNumber: string;
  bankTransitNumber: string;
  isTOSAccepted?: boolean;
  isAcknowledged?: boolean;
}

export interface PADInfoValidation {
  accountNumber?: string;
  bankName?: string;
  bankNumber?: string;
  branchNumber?: string;
  isValid?: boolean;
  message?: string []
  statusCode: number
  transitAddress?: string
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
  passcodeResetEmail?: string
  resetPasscode?: boolean
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
  'Pending' = 'PENDING_APPROVAL',
  'PendingStaffReview'='PENDING_STAFF_REVIEW'
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
  displayOrder: number,
  label: string
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
  statuses: string[]
  name?: string
  page?: number
  limit?: number
  branchName?: string
  id?: string,
  decisionMadeBy?: string
  orgType?: string
  accessType?: string[]
}

export interface OrgPaymentDetails {
  accountId: string
  accountName: string
  bcolAccount: string
  bcolUserId: string
  cfsAccount: CFSAccountDetails
  credit: string
  paymentMethod: string
  statementNotificationEnabled: true
  padTosAcceptedBy:string
  padTosAcceptedDate:string
  futurePaymentMethod: string
}

export interface CFSAccountDetails {
  bankAccountNumber: string
  bankInstitutionNumber: string
  bankTransitNumber: string
  cfsAccountNumber: string
  cfsPartyNumber: string
  cfsSiteNumber: string
  status: string
}

export interface GLInfo {
  client: string;
  responsibilityCentre: string;
  serviceLine: string;
  stob: string;
  projectCode: string;
}

export interface OrgProduct {
  code: string;
  description: string;
  url?: string;
  type?: string;
  subscriptionStatus?: string;
  hidden?:boolean
  premiumOnly?:boolean
  needReview?:boolean
}

export interface OrgProductsRequestBody {
  subscriptions: OrgProductCode[],
}

export interface OrgProductCode {
  productCode: string
}

export interface OrgProductFeeCode {
  amount: number;
  code: string;
}

// Named similiar to Pay-Api
export interface AccountFee {
  product: string;
  applyFilingFees: boolean | string;
  serviceFeeCode: string;
}

export interface AccountFeeDTO {
  product: string;
  applyFilingFees?: string;
  serviceFeeCode?: string;
}

export interface OrgWithAddress {
  name: string;
  id: number;
  addressLine: string;
}

export interface OrgBusinessType {
  name?: string,
  branchName?: string,
  isBusinessAccount?: boolean,
  businessType?: string,
  businessSize?: string
}

export interface PatchOrgPayload {
  action: string;
  statusCode?: string;
  suspensionReasonCode?: string;
  accessType?: string;
}

export interface OrgMap {
  accessType?: string[];
  orgType?: string;
}

export enum OrgAccountTypes {
  ALL = 'All',
  BASIC = 'Basic',
  BASIC_OUT_OF_PROVINCE = 'Basic (out-of-province)',
  PREMIUM = 'Premium',
  PREMIUM_OUT_OF_PROVINCE = 'Premium (out-of-province)',
  GOVM = 'GovM',
  GOVN = 'GovN',
  DIRECTOR_SEARCH = 'Director Search'
}
