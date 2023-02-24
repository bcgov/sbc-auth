<template>
  <v-container class="view-container pt-0">
    <!-- Loading status -->
    <v-fade-transition>
      <div class="loading-container" v-if="isLoading">
        <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
      </div>
    </v-fade-transition>

    <div v-if="!isLoading">
      <!-- Breadcrumbs / Back Navigation -->
      <nav class="crumbs py-6">
        <div>
            <router-link :to="task.relationshipStatus === TaskRelationshipStatusEnum.REJECTED ? pagesEnum.STAFF_DASHBOARD_REJECTED: pagesEnum.STAFF_DASHBOARD_REVIEW">
              <v-icon small color="primary" class="mr-1">mdi-arrow-left</v-icon>
              <span>Back to Staff Dashboard</span>
            </router-link>
        </div>
      </nav>
      <div class="view-header flex-column">
        <h1 class="view-header__title">{{title}}</h1>
        <p class="mt-2 mb-0">Review and verify details for this account.</p>
      </div>
      <v-card class="mt-8" flat>
        <v-row class="mr-0 ml-0">

          <!-- Components list will come here -->
          <v-col class="main-col col-12 col-md-8 pa-6 pa-md-8">
            <template v-for="(component, idx) in componentList">
              <component
                :key="component.id"
                :is="component.component"
                v-bind="component.props"
                v-on="component.events"
                :ref="component.ref"
              />

              <v-divider class="mt-11 mb-8" :key="`divider-${component.id}`"  v-if="idx !== componentList.length-1"></v-divider>
            </template>

            <template v-if="canSelect">
              <v-divider class="mt-11 mb-8" ></v-divider>
              <div class="form-btns d-flex justify-end" >

                <div v-display-mode="!canEdit ? viewOnly : false ">
                  <v-btn large color="primary" class="font-weight-bold mr-2 select-button" @click="openModal()" >
                    <span v-if="isTaskRejected">Re-Approve</span>
                    <span v-else>Approve</span>
                  </v-btn>
                  <v-btn v-if="!isTaskRejected" large outlined color="primary" class="font-weight-bold white--text select-button" @click="openModal(true)"  >
                    <span v-if="isAffidavitReview && !isTaskOnHold">Reject/On Hold</span>
                    <span v-else>Reject</span>
                  </v-btn>
                  <v-btn v-else large outlined color="primary" class="font-weight-bold white--text select-button" @click="openModal(false, false, false, true)"  >
                    <span>Move to pending</span>
                  </v-btn>
                </div>
              </div>
            </template>
          </v-col>

          <!-- Account Status Column -->
          <v-col class="col-12 col-md-4 pl-0 pt-8 pr-8 d-flex">
            <v-divider vertical class="mb-0 mr-8"></v-divider>
            <div class="flex-grow-1">
            <AccountStatusTab
              :taskDetails="task"
              :isPendingReviewPage="isPendingReviewPage"
            />
            </div>
          </v-col>
        </v-row>
        <!-- approve / reject confirmation modals -->
        <AccessRequestModal
          ref="accessRequest"
          :isConfirmationModal="isConfirmationModal"
          :isRejectModal="isRejectModal"
          :isTaskRejected="isTaskRejected"
          :isOnHoldModal="isOnHoldModal"
          :isMoveToPendingModal="isMoveToPendingModal"
          :isSaving="isSaving"
          :orgName="accountUnderReview.name"
          @approve-reject-action="saveSelection"
          @after-confirm-action="goBack()"
          :accountType="taskRelationshipType"
          :taskName="task.type"
          :onholdReasonCodes="onholdReasonCodes"
          />

      </v-card>
    </div>
  </v-container>
</template>

<script lang="ts">
import { AccessType, AffidavitStatus, DisplayModeValues, OnholdOrRejectCode, Pages, TaskAction, TaskRelationshipStatus, TaskRelationshipType, TaskStatus, TaskType } from '@/util/constants'
import { AccountFee, GLInfo, OrgProduct, OrgProductFeeCode, Organization } from '@/models/Organization'
// import { mapActions, mapGetters, mapState } from 'vuex'
import AccessRequestModal from '@/components/auth/staff/review-task/AccessRequestModal.vue'
import AccountAdministrator from '@/components/auth/staff/review-task/AccountAdministrator.vue'
import { AccountInformation } from '@/components/auth/staff/review-task'
import AccountStatusTab from '@/components/auth/staff/review-task/AccountStatus.vue'
import { Address } from '@/models/address'
import { AffidavitInformation } from '@/models/affidavit'
import AgreementInformation from '@/components/auth/staff/review-task/AgreementInformation.vue'
import { Code } from '@/models/Code'
import Component from 'vue-class-component'
import { Contact } from '@/models/contact'
import DocumentService from '@/services/document.services'
import DownloadAffidavit from '@/components/auth/staff/review-task/DownloadAffidavit.vue'
import NotaryInformation from '@/components/auth/staff/review-task/NotaryInformation.vue'
import PaymentInformation from '@/components/auth/staff/review-task/PaymentInformation.vue'
import ProductFee from '@/components/auth/staff/review-task/ProductFee.vue'
import { Prop } from 'vue-property-decorator'
import StaffModuleStore from '@/store/modules/staff'
import { Task } from '@/models/Task'
import { User } from '@/models/user'

import Vue from 'vue'
import { getModule } from 'vuex-module-decorators'
import { namespace } from 'vuex-class'
import { or } from 'vuelidate/lib/validators'

const StaffModule = namespace('staff')
const TaskModule = namespace('task')
const orgModule = namespace('org')
const CodesModule = namespace('codes')

@Component({
  components: {
    DownloadAffidavit,
    AccountInformation,
    AccountAdministrator,
    NotaryInformation,
    AccountStatusTab,
    AccessRequestModal
  }
})
export default class ReviewAccountView extends Vue {
  @Prop() orgId: number // chnage varible name to taskId

  @TaskModule.Action('getTaskById') public getTaskById!:(orgId: number) =>Promise<Task>

  @StaffModule.State('accountUnderReview') public accountUnderReview!: Organization
  @StaffModule.State('accountUnderReviewAdmin') public accountUnderReviewAdmin!: User
  @StaffModule.State('accountUnderReviewAddress') public accountUnderReviewAddress!: Address
  @StaffModule.State('accountUnderReviewAdminContact') public accountUnderReviewAdminContact!: Contact
  @StaffModule.State('accountUnderReviewAffidavitInfo') public accountUnderReviewAffidavitInfo!: AffidavitInformation

  @StaffModule.Getter('accountNotaryName') public accountNotaryName!: string

  @StaffModule.Action('syncTaskUnderReview') public syncTaskUnderReview!: (task:Task) => Promise<void>
  @StaffModule.Action('approveAccountUnderReview') public approveAccountUnderReview!: (task:Task) => Promise<void>
  @StaffModule.Action('rejectorOnHoldAccountUnderReview') public rejectorOnHoldAccountUnderReview!: (task:any) => Promise<void>

  @orgModule.Action('fetchCurrentOrganizationGLInfo') public fetchCurrentOrganizationGLInfo!:(accountId: number) =>Promise<any>
  @orgModule.State('currentOrgGLInfo') public currentOrgGLInfo!: GLInfo
  @orgModule.Action('fetchOrgProductFeeCodes') public fetchOrgProductFeeCodes!:() =>Promise<OrgProductFeeCode>
  @orgModule.Action('getOrgProducts') public getOrgProducts!:(accountId: number) =>Promise<OrgProduct[]>
  @orgModule.Action('createAccountFees') public createAccountFees!:(accoundId:number) =>Promise<any>
  @orgModule.Action('syncCurrentAccountFees') public syncCurrentAccountFees!:(accoundId:number) =>Promise<AccountFee[]>
  @orgModule.Mutation('resetCurrentAccountFees') public resetCurrentAccountFees!:() =>void
  @orgModule.Action('updateOrganizationAccessType') updateOrganizationAccessType!:({ accessType, orgId, syncOrg }) => Promise<boolean>

  @CodesModule.Action('getOnholdReasonCodes') public getOnholdReasonCodes!: () => Promise<Code[]>
  @CodesModule.State('onholdReasonCodes') private readonly onholdReasonCodes!: Code[]

  private staffStore = getModule(StaffModuleStore, this.$store)
  public isLoading = true
  public isSaving = false

  private readonly pagesEnum = Pages
  private readonly TaskRelationshipStatusEnum = TaskRelationshipStatus

  private isConfirmationModal:boolean = false
  private isRejectModal:boolean = false
  private isOnHoldModal:boolean = false
  private isMoveToPendingModal:boolean = false
  public task :Task
  public taskRelationshipType:string = ''
  private productFeeFormValid: boolean = false
  private viewOnly = DisplayModeValues.VIEW_ONLY
  accountInfoAccessType: AccessType = null
  accountInfoValid = true
  showAccountInfoValidations = false

  $refs: {
    accessRequest: AccessRequestModal,
    productFeeRef: HTMLFormElement
  }

  private get canEdit (): boolean {
    return this.task.status === TaskStatus.OPEN || this.isTaskOnHold ||
           (this.task.status === TaskStatus.COMPLETED && this.task.relationshipStatus === TaskRelationshipStatus.REJECTED)
  }

  private get isTaskOnHold (): boolean {
    return this.task.status === TaskStatus.HOLD
  }

  private get isTaskRejected (): boolean {
    return this.task.relationshipStatus === TaskRelationshipStatus.REJECTED
  }

  private get canSelect (): boolean {
    return (this.task.relationshipStatus === TaskRelationshipStatus.PENDING_STAFF_REVIEW ||
            (this.task.relationshipType === TaskRelationshipType.PRODUCT &&
            this.task.relationshipStatus === TaskRelationshipStatus.REJECTED))
  }

  private get isPendingReviewPage () {
    return this.task.relationshipStatus === TaskRelationshipStatus.PENDING_STAFF_REVIEW
  }

  // Tasks with Affidavit action can be put on hold
  private get isAffidavitReview (): boolean {
    return this.task.action === TaskAction.AFFIDAVIT_REVIEW
  }

  private get isGovNAccountReview (): boolean {
    return this.task.type === TaskType.GOVN_REVIEW
  }

  get title () {
    let title = 'Review Account'
    if (this.taskRelationshipType === TaskRelationshipType.PRODUCT) {
      title = `Access Request (${this.task.type})`
    } else if (this.taskRelationshipType === TaskRelationshipType.USER) {
      // For now, Task with relationship type as user is for BCeID Admin request
      title = 'Review BCeID Admin'
    }
    return title
  }

  /*
    5 types of Tasks:
    1. New BCeId Account creation -> TaskType.NEW_ACCOUNT_STAFF_REVIEW and TaskRelationshipType.ORG and AFFIDAVIT_REVIEW action
    2. Product request access -> TaskType.PRODUCT and taskRelationshipType === TaskRelationshipType.PRODUCT and PRODUCT_REVIEW action
    3. GovM review -> TaskType.GOVM and TaskRelationshipType.ORG and ACCOUNT_REVIEW action
    4. BCeId admin review -> TaskType.BCeID Admin and TaskRelationshipType.USER and ACCOUNT_REVIEW action
    5. GovN review -> 1. Bcsc flow: TaskType.GOVN_REVIEW and TaskRelationshipType.ORG and ACCOUNT_REVIEW action
                      2. Bceid flow: TaskType.GOVN_REVIEW and TaskRelationshipType.ORG and AFFIDAVIT_REVIEW action
  */
  get componentList () {
    const taskType = this.task.type
    console.log('taskType', taskType)
    switch (taskType) {
      case TaskType.GOVM_REVIEW:
        return [{ ...this.componentAccountInformation(1) },
          { ...this.componentAccountAdministrator(2) },
          { ...this.componentPaymentInformation(3) },
          { ...this.componentProductFee(4) }
        ]
      case TaskType.NEW_ACCOUNT_STAFF_REVIEW:
        return [{ ...this.compDownloadAffidavit(1) },
          { ...this.componentAccountInformation(2) },
          { ...this.componentAccountAdministrator(3) },
          { ...this.componentNotaryInformation(4) }
        ]
      case TaskType.BCEID_ADMIN_REVIEW:
        return [{ ...this.compDownloadAffidavit(1) },
          { ...this.componentAccountInformation(2) },
          { ...this.componentAccountAdministrator(3) },
          { ...this.componentNotaryInformation(4) }
        ]
      case TaskType.GOVN_REVIEW:
        let list = []
        if (this.task.action === TaskAction.ACCOUNT_REVIEW) {
          list = [{ ...this.componentAccountInformation(1) },
            { ...this.componentAccountAdministrator(2) },
            { ...this.componentProductFee(3) }
          ]
        } else {
          list = [{ ...this.compDownloadAffidavit(1) },
            { ...this.componentAccountInformation(2) },
            { ...this.componentAccountAdministrator(3) },
            { ...this.componentNotaryInformation(4) },
            { ...this.componentProductFee(5) }
          ]
        }
        // if account access type was changed to regular remove the product fee comp
        if (this.accountInfoAccessType === AccessType.REGULAR) list.pop()
        return list
      default:
        // Since task of Product type has variable Task Type (eg, Wills Registry, PPR ) we specify in default.
        // Also, we double check by task relationship type
        if (this.taskRelationshipType === TaskRelationshipType.PRODUCT) {
          return [
            { ...this.componentAccountInformation(1) },
            { ...this.componentAccountAdministrator(2) },
            { ...this.componentAgreementInformation(3) }
          ]
        }
        break
    }
  }

  private async mounted () {
    // need to change call task api before

    try {
      this.task = await this.getTaskById(this.orgId)
      this.taskRelationshipType = this.task.relationshipType
      await this.syncTaskUnderReview(this.task)

      // If the task type is GOVM or GOVN, then need to populate product fee codes
      if (this.task.type === TaskType.GOVM_REVIEW || this.task.type === TaskType.GOVN_REVIEW) {
        const accountId = this.task.relationshipId
        await this.fetchCurrentOrganizationGLInfo(accountId)
        await this.fetchOrgProductFeeCodes()
        await this.getOrgProducts(accountId)
        // For rejected accounts view
        if (!this.canSelect) {
          await this.syncCurrentAccountFees(accountId)
        } else {
          this.resetCurrentAccountFees()
        }
      }
      // Tasks with Affidavit action can be put on hold. Therefore, populate on hold reasons
      if (this.isAffidavitReview && (!this.onholdReasonCodes || this.onholdReasonCodes.length === 0)) {
        await this.getOnholdReasonCodes()
      }
    } catch (ex) {
      // eslint-disable-next-line no-console
      console.error(ex)
    } finally {
      this.isLoading = false
    }
  }

  private async downloadAffidavit (): Promise<void> {
    // Invoke document service to get affidavit for current organization
    await DocumentService.getSignedAffidavit(this.accountUnderReviewAffidavitInfo?.documentUrl, `${this.accountUnderReview.name}-affidavit`)
  }

  private openModal (isRejectModal:boolean = false, isConfirmationModal: boolean = false, rejectConfirmationModal:boolean = false, isMoveToPendingModal: boolean = false) {
    console.log('isMoveToPendingModal', isMoveToPendingModal)
    if (!this.accountInfoValid) {
      this.showAccountInfoValidations = true
      window.scrollTo({ top: 200, behavior: 'smooth' })
      return false
    }
    if (this.task.type === TaskType.GOVM_REVIEW && !this.productFeeFormValid) {
      // validate form before showing pop-up
      (this.$refs.productFeeRef[0] as any).validateNow()
      if (!this.productFeeFormValid) {
        return false
      }
    }
    this.isConfirmationModal = isConfirmationModal

    if (rejectConfirmationModal || (isRejectModal && this.isTaskOnHold)) {
      this.isRejectModal = true
      this.isOnHoldModal = false
    } else if (!isMoveToPendingModal) {
      this.isRejectModal = this.isAffidavitReview ? false : isRejectModal
      this.isOnHoldModal = this.isAffidavitReview ? isRejectModal : false
    } else {
      this.isMoveToPendingModal = true
    }

    if (isConfirmationModal) {
      this.$refs.accessRequest.close()
      this.$refs.accessRequest.openConfirm()
    } else {
      this.$refs.accessRequest.open()
      this.$refs.accessRequest.closeConfirm()
    }
  }

  private async saveSelection (reason): Promise<void> {
    const { isValidForm, accountToBeOnholdOrRejected, onholdReasons } = reason

    if (isValidForm) {
      this.isSaving = true
      // if account approve
      const isApprove = !this.isRejectModal && !this.isOnHoldModal
      // on rejecting there will be two scenarios
      // 1. by clicking reject for normal flow.
      // 2. by selecting remark as Reject account ,(check by using code)
      // both cases we need to call reject API than hold
      const isRejecting = this.isRejectModal || accountToBeOnholdOrRejected === OnholdOrRejectCode.REJECTED
      try {
        if (this.accountInfoAccessType && this.accountInfoAccessType !== this.accountUnderReview.accessType) {
          const success = await this.updateOrganizationAccessType({ accessType: this.accountInfoAccessType as string, orgId: this.accountUnderReview.id, syncOrg: false })
          if (!success) throw new Error('Error updating account access type prevented review completion.')
        }
        if (isApprove) {
          await this.approveAccountUnderReview(this.task)
        } else {
        // both reject and hold will happen here passing second argument to determine which call need to make
          await this.rejectorOnHoldAccountUnderReview({ task: this.task, isRejecting, remarks: onholdReasons })
        }
        const taskType: any = this.task.type

        if (
          [TaskType.GOVM_REVIEW, TaskType.GOVN_REVIEW].includes(taskType) &&
          (!this.accountInfoAccessType || [AccessType.GOVN, AccessType.GOVM].includes(this.accountInfoAccessType))
        ) {
          await this.createAccountFees(this.task.relationshipId)
        }
        this.openModal(!isApprove, true, isRejecting)
      // this.$router.push(Pages.STAFF_DASHBOARD)
      } catch (error) {
      // eslint-disable-next-line no-console
        console.log(error)
      } finally {
        this.isSaving = false
      }
    }
  }

  public get accountNotaryContact (): Contact {
    return this.accountUnderReviewAffidavitInfo?.contacts?.length > 0 && this.accountUnderReviewAffidavitInfo?.contacts[0]
  }

  private goBack (): void {
    this.$router.push(Pages.STAFF_DASHBOARD)
  }

  private productFeeChange (isFormValid): void {
    this.productFeeFormValid = isFormValid
  }

  formattedComponent (tabNumber, id, component, props, event = null, ref = null) {
    return {
      id: id,
      component: component,
      props: {
        tabNumber: tabNumber,
        ...props
      },
      events: { ...event },
      ref: ref
    }
  }

  // list of components
  compDownloadAffidavit (tabNumber:number = 1) {
    let subTitle = 'Download the notarized affidavit associated with this account to verify the account creators identity and associated information.'
    if (this.accountUnderReviewAffidavitInfo?.status === AffidavitStatus.APPROVED) {
      subTitle = 'Download the notarized affidavit associated with this account that has been reviewed and approved.'
    }
    return this.formattedComponent(
      tabNumber,
      `download-affidavit-${tabNumber}`,
      DownloadAffidavit,
      {
        title: 'Download Affidavit',
        subTitle: subTitle,
        affidavitName: this.accountUnderReview.name
      },
      { 'emit-download-affidavit': this.downloadAffidavit }
    )
  }

  componentAccountInformation (tabNumber:number = 1) {
    return this.formattedComponent(
      tabNumber,
      `account-info-${tabNumber}`,
      AccountInformation,
      {
        title: 'Account Information',
        accountUnderReview: this.accountUnderReview,
        accountUnderReviewAddress: this.accountUnderReviewAddress,
        isGovnReview: this.isGovNAccountReview,
        showValidations: this.showAccountInfoValidations
      },
      {
        'emit-access-type': (event: AccessType) => { this.accountInfoAccessType = event },
        'emit-valid': (event: boolean) => { this.accountInfoValid = event }
      }
    )
  }
  componentAccountAdministrator (tabNumber:number = 1) {
    return this.formattedComponent(
      tabNumber,
      `account-administration-${tabNumber}`,
      AccountAdministrator,
      {
        title: 'Account Administrator',
        accountUnderReviewAdmin: this.accountUnderReviewAdmin,
        accountUnderReviewAdminContact: this.accountUnderReviewAdminContact
      }

    )
  }

  componentNotaryInformation (tabNumber:number = 1) {
    return this.formattedComponent(tabNumber,
      `notary-info-${tabNumber}`,
      NotaryInformation,
      {
        title: 'Notary Information',
        accountNotaryContact: this.accountNotaryContact,
        accountNotaryName: this.accountUnderReviewAffidavitInfo?.issuer || '-'
      }
    )
  }
  componentAgreementInformation (tabNumber:number = 1) {
    return this.formattedComponent(tabNumber,
      `agreement-info-${tabNumber}`,
      AgreementInformation,
      {
        title: 'Agreement',
        isTOSAlreadyAccepted: true,
        orgName: this.accountUnderReview.name,
        userName: `${this.accountUnderReviewAdmin.firstname} ${this.accountUnderReviewAdmin.lastname}`
      }
    )
  }
  componentPaymentInformation (tabNumber:number = 1) {
    return this.formattedComponent(tabNumber,
      `payment-info-${tabNumber}`,
      PaymentInformation,
      {
        title: 'Payment Information',
        currentOrganizationGLInfo: this.currentOrgGLInfo
      }
    )
  }
  componentProductFee (tabNumber:number = 1) {
    return this.formattedComponent(tabNumber,
      `product-fee-${tabNumber}`,
      ProductFee,
      {
        title: 'Product Fee',
        canSelect: this.canSelect
      },
      { 'emit-product-fee-change': this.productFeeChange },
      'productFeeRef'
    )
  }
}
</script>

<style lang="scss" scoped>

  .select-button {
    width: 8.75rem;
  }

  .crumbs a {
    font-size: 0.875rem;
    text-decoration: none;

    i {
      margin-top: -2px;
    }
  }

  .crumbs a:hover {
    span {
      text-decoration: underline;
    }
  }
</style>
