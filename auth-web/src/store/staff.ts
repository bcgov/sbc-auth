import { AccountStatus, AffidavitStatus, TaskAction, TaskRelationshipStatus, TaskRelationshipType, TaskType } from '@/util/constants'
import { AccountType, GLCode, ProductCode } from '@/models/Staff'
import { MembershipType, OrgFilterParams, Organization } from '@/models/Organization'
import { SyncAccountPayload, Task } from '@/models/Task'
import { computed, reactive } from '@vue/composition-api'

import { Address } from '@/models/address'
import { AffidavitInformation } from '@/models/affidavit'
import { Contact } from '@/models/contact'
import { Invitation } from '@/models/Invitation'
import InvitationService from '@/services/invitation.services'
import OrgService from '@/services/org.services'
import PaymentService from '@/services/payment.services'
import StaffService from '@/services/staff.services'
import TaskService from '@/services/task.services'
import { User } from '@/models/user'
import UserService from '@/services/user.services'
import { defineStore } from 'pinia'

export const useStaffStore = defineStore('staff', () => {
  const state = reactive({
    accountTypes: [] as AccountType[],
    accountUnderReview: {} as Organization,
    accountUnderReviewAddress: {} as Address,
    accountUnderReviewAdmin: {} as User,
    accountUnderReviewAdminContact: {} as Contact,
    accountUnderReviewAffidavitInfo: {} as AffidavitInformation,
    activeStaffOrgs: [] as Organization[],
    pendingInvitationOrgs: [] as Organization[],
    pendingStaffOrgs: [] as Organization[],
    products: [] as ProductCode[],
    rejectedStaffOrgs: [] as Organization[],
    suspendedReviewTotal: 0,
    suspendedStaffOrgs: [] as Organization[]
  })

  const accountNotaryName = computed<string>(() => {
    return state.accountUnderReviewAffidavitInfo?.issuer || '-'
  })

  const accountNotaryContact = computed<Contact>(() => {
    return state.accountUnderReviewAffidavitInfo?.contacts?.length > 0 &&
      state.accountUnderReviewAffidavitInfo?.contacts[0]
  })

  const rejectedReviewCount = computed<number>(() => {
    return state.rejectedStaffOrgs?.length || 0
  })

  const pendingInvitationsCount = computed<number>(() => {
    return state.pendingInvitationOrgs?.length || 0
  })

  const suspendedReviewCount = computed<number>(() => {
    return state.suspendedReviewTotal || 0
  })

  async function getProducts (): Promise<ProductCode[]> {
    const response = await StaffService.getProducts()
    if (response?.data && response.status === 200) {
      state.products = response.data
      return response.data
    }
  }

  async function getAccountTypes (): Promise<AccountType[]> {
    const response = await StaffService.getAccountTypes()
    if (response?.data && response.status === 200) {
      state.accountTypes = response.data
      return response.data
    }
  }

  async function syncAccountUnderReview (syncAccountPayload: SyncAccountPayload): Promise<void> {
    const accountResponse = await OrgService.getOrganization(syncAccountPayload.organizationIdentifier)
    if (accountResponse?.data && accountResponse?.status === 200) {
      state.accountUnderReview = accountResponse.data

      const addressResponse = await OrgService.getContactForOrg(syncAccountPayload.organizationIdentifier)
      if (addressResponse) {
        state.accountUnderReviewAddress = addressResponse
      }
      // If BCeIdAdmin request flow, get the requesting admin details rather than current account admin
      if (syncAccountPayload.isBCeIDAdminReview) {
        const user = syncAccountPayload.relatedBCeIDUser
        state.accountUnderReviewAdmin = user
        if (user.contacts && user.contacts.length > 0) {
          state.accountUnderReviewAdminContact = user.contacts[0]
        }
      } else {
        const accountMembersResponse = await OrgService.getOrgMembers(syncAccountPayload.organizationIdentifier, 'ACTIVE')
        if (accountMembersResponse?.data && accountMembersResponse?.status === 200) {
          const admin = accountMembersResponse.data.members.find(member => member.membershipTypeCode === MembershipType.Admin)?.user
          if (admin) {
            state.accountUnderReviewAdmin = admin
            const adminContactResponse = await UserService.getUserProfile(admin.username)
            if (adminContactResponse?.data && adminContactResponse?.status === 200) {
              const contact = adminContactResponse?.data?.contacts?.length > 0 && adminContactResponse?.data?.contacts[0]
              if (contact) {
                state.accountUnderReviewAdminContact = contact
              }
            }
          }
        }
      }
    }
  }

  async function syncTaskUnderReview (task:Task): Promise<void> {
    const taskRelationshipType = task.relationshipType
    const taskRelationshipId = task.relationshipId
    const taskAccountId = task.accountId
    const taskAction = task.action

    const accountId = taskRelationshipType === TaskRelationshipType.ORG ? taskRelationshipId : taskAccountId
    const syncAccountPayload: SyncAccountPayload = {
      organizationIdentifier: accountId,
      isBCeIDAdminReview: task.type === TaskType.BCEID_ADMIN_REVIEW,
      relatedBCeIDUser: task.user
    }
    await syncAccountUnderReview(syncAccountPayload)
    if (taskAction === TaskAction.AFFIDAVIT_REVIEW) {
      await syncAccountAffidavit(task)
    }
  }

  async function syncAccountAffidavit (task: Task): Promise<void> {
    const taskUserGuid = task?.user?.keycloakGuid
    let status = task.relationshipStatus

    switch (task.relationshipStatus) {
      case TaskRelationshipStatus.PENDING_STAFF_REVIEW:
        status = null // This looks at pending and approved one or none.
        break
      case TaskRelationshipStatus.REJECTED:
        status = AffidavitStatus.REJECTED
        break
      default:
        status = AffidavitStatus.APPROVED
        break
    }

    const affidavitResponse = await UserService.getAffidavitInfo(taskUserGuid, status)
    if (affidavitResponse?.data && affidavitResponse?.status === 200) {
      state.accountUnderReviewAffidavitInfo = affidavitResponse.data
    }
  }

  async function approveAccountUnderReview (task:Task) {
    if (task) {
      const response = await TaskService.approvePendingTask(task)
      const newTask = response.data || task
      await syncTaskUnderReview(newTask)
    }
  }

  async function rejectorOnHoldAccountUnderReview ({ task, isRejecting, remarks }) {
    if (task) {
      const taskId = task.id
      let newTask = null
      if (isRejecting) {
        const response = await TaskService.rejectPendingTask(taskId)
        newTask = response.data || task
      } else {
        const response = await TaskService.onHoldPendingTask(taskId, remarks)
        newTask = response.data || task
      }
      await syncTaskUnderReview(newTask)
    }
  }

  async function syncActiveStaffOrgs () {
    const response = await StaffService.getStaffOrgs(AccountStatus.ACTIVE)
    state.activeStaffOrgs = response?.data?.orgs || []
    return response?.data?.orgs || []
  }

  async function syncPendingInvitationOrgs () {
    const response = await StaffService.getStaffOrgs(AccountStatus.PENDING_ACTIVATION)
    const result = response?.data?.orgs || []
    state.pendingInvitationOrgs = result
    return result
  }

  async function syncRejectedStaffOrgs () {
    const response = await StaffService.getStaffOrgs(AccountStatus.REJECTED)
    state.rejectedStaffOrgs = response?.data?.orgs || []
    return response?.data?.orgs || []
  }

  async function syncSuspendedStaffOrgs () {
    const response:any = await StaffService.getStaffOrgs(AccountStatus.NSF_SUSPENDED)
    state.suspendedReviewTotal = response?.data?.total
    state.pendingInvitationOrgs = response?.data?.orgs || []
    return response?.data?.orgs || []
  }

  async function searchOrgs (filterParams: OrgFilterParams) {
    const response = await StaffService.searchOrgs(filterParams)
    if (response?.data) {
      return {
        limit: response.data.limit,
        page: response.data.page,
        total: response.data.total,
        orgs: response.data.orgs
      }
    }
    return {}
  }

  async function syncPendingStaffOrgs () {
    const response = await StaffService.getStaffOrgs(AccountStatus.PENDING_STAFF_REVIEW)
    state.pendingStaffOrgs = response?.data?.orgs || []
    return response?.data?.orgs || []
  }

  async function resendPendingOrgInvitation (invitation: Invitation) {
    return InvitationService.resendInvitation(invitation)
  }

  async function deleteOrg (org: Organization) {
    const invResponse = await InvitationService.deleteInvitation(org.invitations[0].id)
    if (!invResponse || invResponse.status !== 200 || !invResponse.data) {
      throw Error('Unable to delete invitation')
    }
    const orgResponse = await OrgService.deactivateOrg(org.id)
    if (!orgResponse || orgResponse.status !== 204) {
      throw Error('Unable to delete org')
    }
  }

  async function getGLCodeList () {
    const response = await PaymentService.getGLCodeList()
    return response?.data?.items || []
  }

  async function getGLCodeFiling (distributionCodeId: number) {
    const response = await PaymentService.getGLCodeFiling(distributionCodeId)
    return response?.data?.items || []
  }

  async function getGLCode (distributionCodeId: number) {
    const response = await PaymentService.getGLCode(distributionCodeId)
    return response?.data || {}
  }

  async function updateGLCodeFiling (glcodeFilingData: GLCode) {
    // Update service fee information first, and then the main GL code.
    let serviceFeeGlCode : number = null
    if (glcodeFilingData.serviceFee) {
      const serviceFeeResponse = await PaymentService.updateGLCodeFiling(glcodeFilingData.serviceFee)
      serviceFeeGlCode = serviceFeeResponse?.data?.distributionCodeId
    }
    glcodeFilingData.serviceFeeDistributionCodeId = serviceFeeGlCode
    const response = await PaymentService.updateGLCodeFiling(glcodeFilingData)
    return response?.data || {}
  }

  return {
    accountNotaryContact,
    accountNotaryName,
    approveAccountUnderReview,
    deleteOrg,
    getAccountTypes,
    getGLCode,
    getGLCodeList,
    getGLCodeFiling,
    getProducts,
    pendingInvitationsCount,
    rejectedReviewCount,
    rejectorOnHoldAccountUnderReview,
    resendPendingOrgInvitation,
    searchOrgs,
    state,
    suspendedReviewCount,
    syncTaskUnderReview,
    syncAccountAffidavit,
    syncAccountUnderReview,
    syncActiveStaffOrgs,
    syncPendingInvitationOrgs,
    syncRejectedStaffOrgs,
    syncSuspendedStaffOrgs,
    syncPendingStaffOrgs,
    updateGLCodeFiling
  }
})
