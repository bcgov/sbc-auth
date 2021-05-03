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
              />
              <v-divider class="mt-11 mb-8" :key="`divider-${component.id}`"  v-if="idx !== componentList.length-1"></v-divider>
            </template>
            <template v-if="canSelect" >
              <v-divider class="mt-11 mb-8" ></v-divider>
              <div class="form-btns d-flex justify-end" >

                <div>
                  <v-btn large color="success" class="font-weight-bold mr-2 select-button" @click="openModal()">
                    <span>Approve</span>
                  </v-btn>
                  <v-btn large outlined color="red" class="font-weight-bold white--text select-button" @click="openModal(true)">
                    <span>Reject</span>
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
          :isSaving="isSaving"
          :orgName="accountUnderReview.name"
          @approve-reject-action="saveSelection()"
          @after-confirm-action="goBack()"
          :accountType="taskRelationshipType"
          :taskName="task.type"
          />

      </v-card>
    </div>
  </v-container>
</template>

<script lang="ts">
import { AccountFee, AccountFeeDTO, GLInfo, OrgProduct, OrgProductFeeCode, Organization } from '@/models/Organization'
import { Pages, TaskRelationshipStatus, TaskRelationshipType, TaskType } from '@/util/constants'
// import { mapActions, mapGetters, mapState } from 'vuex'
import AccessRequestModal from '@/components/auth/staff/review-task/AccessRequestModal.vue'
import AccountAdministrator from '@/components/auth/staff/review-task/AccountAdministrator.vue'
import AccountInformation from '@/components/auth/staff/review-task/AccountInformation.vue'
import AccountStatusTab from '@/components/auth/staff/review-task/AccountStatus.vue'
import { Address } from '@/models/address'
import { AffidavitInformation } from '@/models/affidavit'
import AgreementInformation from '@/components/auth/staff/review-task/AgreementInformation.vue'
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

const StaffModule = namespace('staff')
const TaskModule = namespace('task')
const orgModule = namespace('org')

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
  @StaffModule.Getter('accountNotaryContact') public accountNotaryContact!: Contact

  @StaffModule.Action('syncTaskUnderReview') public syncTaskUnderReview!: (task:Task) => Promise<void>
  @StaffModule.Action('approveAccountUnderReview') public approveAccountUnderReview!: (task:Task) => Promise<void>
  @StaffModule.Action('rejectAccountUnderReview') public rejectAccountUnderReview!: (task:Task) => Promise<void>

  @orgModule.Action('fetchCurrentOrganizationGLInfo') public fetchCurrentOrganizationGLInfo!:(accountId: number) =>Promise<any>
  @orgModule.State('currentOrgGLInfo') public currentOrgGLInfo!: GLInfo
  @orgModule.Action('fetchOrgProductFeeCodes') public fetchOrgProductFeeCodes!:() =>Promise<OrgProductFeeCode>
  @orgModule.Action('getOrgProducts') public getOrgProducts!:(accountId: number) =>Promise<OrgProduct[]>
  @orgModule.Action('createAccountFees') public createAccountFees!:(accoundId:number) =>Promise<any>
  @orgModule.Action('syncCurrentAccountFees') public syncCurrentAccountFees!:(accoundId:number) =>Promise<AccountFee[]>

  private staffStore = getModule(StaffModuleStore, this.$store)
  public isLoading = true
  public isSaving = false

  private readonly pagesEnum = Pages
  private readonly TaskRelationshipStatusEnum = TaskRelationshipStatus

  private isConfirmationModal:boolean = false
  private isRejectModal:boolean = false
  public task :Task
  public taskRelationshipType:string = ''
  private productFeeFormValid: boolean = false

  $refs: {
    accessRequest: AccessRequestModal,
  }

  private get canSelect (): boolean {
    return this.task.relationshipStatus === TaskRelationshipStatus.PENDING_STAFF_REVIEW
  }

  private get isPendingReviewPage () {
    return this.task.relationshipStatus === TaskRelationshipStatus.PENDING_STAFF_REVIEW
  }

  get title () {
    let title = 'Review Account'
    if (this.taskRelationshipType === TaskRelationshipType.PRODUCT) {
      title = `Access Request (${this.task.type})`
    }
    return title
  }
  get componentList () {
    if (this.taskRelationshipType === TaskRelationshipType.PRODUCT) {
      return [
        { ...this.componentAccountInformation(1) },
        { ...this.componentAccountAdministrator(2) },
        { ...this.componentAgreementInformation(3) }
      ]
    } else {
      if (this.task.type === TaskType.NEW_ACCOUNT_STAFF_REVIEW) {
        return [{ ...this.compDownloadAffidavit(1) },
          { ...this.componentAccountInformation(2) },
          { ...this.componentAccountAdministrator(3) },
          { ...this.componentNotaryInformation(4) }
        ]
      } else {
        // For GovM accounts
        return [{ ...this.componentAccountInformation(1) },
          { ...this.componentAccountAdministrator(2) },
          { ...this.componentPaymentInformation(3) },
          { ...this.componentProductFee(4) }
        ]
      }
    }
  }

  private async mounted () {
    // need to change call task api before

    try {
      this.task = await this.getTaskById(this.orgId)
      this.taskRelationshipType = this.task.relationshipType
      await this.syncTaskUnderReview(this.task)

      if (this.task.type === TaskType.GOVM_REVIEW) {
        const accountId = this.task.relationshipId
        await this.fetchCurrentOrganizationGLInfo(accountId)
        await this.fetchOrgProductFeeCodes()
        await this.getOrgProducts(accountId)
        // For rejected accounts view
        if (!this.canSelect) {
          await this.syncCurrentAccountFees(accountId)
        }
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

  private openModal (isRejectModal:boolean = false, isConfirmationModal: boolean = false) {
    if (this.task.type === TaskType.GOVM_REVIEW && !this.productFeeFormValid) {
      return
    }
    this.isConfirmationModal = isConfirmationModal
    this.isRejectModal = isRejectModal

    if (isConfirmationModal) {
      this.$refs.accessRequest.close()
      this.$refs.accessRequest.openConfirm()
    } else {
      this.$refs.accessRequest.open()
      this.$refs.accessRequest.closeConfirm()
    }
  }

  private async saveSelection (): Promise<void> {
    this.isSaving = true
    try {
      if (!this.isRejectModal) {
        await this.approveAccountUnderReview(this.task)
      } else {
        await this.rejectAccountUnderReview(this.task)
      }
      if (this.task.type === TaskType.GOVM_REVIEW) {
        await this.createAccountFees(this.task.relationshipId)
      }
      this.openModal(this.isRejectModal, true)
      // this.$router.push(Pages.STAFF_DASHBOARD)
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log(error)
    } finally {
      this.isSaving = false
    }
  }

  private goBack (): void {
    this.$router.push(Pages.STAFF_DASHBOARD)
  }

  private productFeeChange (isFormValid): void {
    this.productFeeFormValid = isFormValid
  }

  formattedComponent (tabNumber, id, component, props, event = null) {
    return {
      id: id,
      component: component,
      props: {
        tabNumber: tabNumber,
        ...props
      },
      events: { ...event }
    }
  }

  // list of components
  compDownloadAffidavit (tabNumber:number = 1) {
    return this.formattedComponent(
      tabNumber,
      `download-affidavit-${tabNumber}`,
      DownloadAffidavit,
      {
        title: 'Download Affidavit',
        subTitle: 'Download the notarized affidavit associated with this account to verify the account creators identity and associated information.',
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
        accountUnderReviewAddress: this.accountUnderReviewAddress
      },
      null
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
        accountNotaryName: this.accountNotaryName
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
      { 'emit-product-fee-change': this.productFeeChange }
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
