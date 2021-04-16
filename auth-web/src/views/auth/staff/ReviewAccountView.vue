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
        <h1 class="view-header__title">Review Account</h1>
        <p class="mt-2 mb-0">Review and verify details for this account.</p>
      </div>
      <v-card class="mt-8" flat>
        <v-row class="mr-0 ml-0">

          <!-- Components list will come here -->
          <v-col class="main-col col-12 col-md-8 pa-6 pa-md-8">
            <template v-for="(component) in componentList">
              <component
                :key="component.id"
                :is="component.component"
                v-bind="component.props"
                v-on="component.events"
              />
              <v-divider class="mt-11 mb-8" :key="`divider-${component.id}`" ></v-divider>
            </template>

              <div class="form-btns d-flex justify-end" v-if="canSelect" >
                <div>
                  <v-btn large color="success" class="font-weight-bold mr-2 select-button" @click="openModal()">
                    <span>Approve</span>
                  </v-btn>
                  <v-btn large outlined color="red" class="font-weight-bold white--text select-button" @click="openModal(true)">
                    <span>Reject</span>
                  </v-btn>
                </div>
              </div>
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
          />

      </v-card>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Pages, TaskRelationshipStatus, TaskRelationshipType } from '@/util/constants'

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
import { Organization } from '@/models/Organization'
import { Prop } from 'vue-property-decorator'
import StaffModuleStore from '@/store/modules/staff'
import { Task } from '@/models/task'
import { User } from '@/models/user'

import Vue from 'vue'
import { getModule } from 'vuex-module-decorators'
import { namespace } from 'vuex-class'

const StaffModule = namespace('staff')
const TaskModule = namespace('task')

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
  @StaffModule.Getter('affidavitDocumentUrl') public affidavitDocumentUrl!: string

  @StaffModule.Action('syncTaskUnderReview') public syncTaskUnderReview!: (task:Task) => Promise<void>
  @StaffModule.Action('approveAccountUnderReview') public approveAccountUnderReview!: (task:Task) => Promise<void>
  @StaffModule.Action('rejectAccountUnderReview') public rejectAccountUnderReview!: (task:Task) => Promise<void>

  private staffStore = getModule(StaffModuleStore, this.$store)
  public isLoading = true
  public isSaving = false

  private readonly pagesEnum = Pages
  private readonly TaskRelationshipStatusEnum = TaskRelationshipStatus

  private isConfirmationModal:boolean = false
  private isRejectModal:boolean = false
  public task :Task
  public taskrRelationshipType:string = ''

  $refs: {
    accessRequest: AccessRequestModal,
  }

  private get canSelect (): boolean {
    return this.task.relationshipStatus === TaskRelationshipStatus.PENDING_STAFF_REVIEW
  }

  private get isPendingReviewPage () {
    return this.task.relationshipStatus === TaskRelationshipStatus.PENDING_STAFF_REVIEW
  }

  get componentList () {
    if (this.taskrRelationshipType === TaskRelationshipType.PRODUCT) {
      return [
        { ...this.componentAccountInformation(1) },
        { ...this.componentAccountAdministrator(2) },
        { ...this.componentAgreementInformation(3) }
      ]
    } else {
      return [{ ...this.compDownloadAffidavit(1) },
        { ...this.componentAccountInformation(2) },
        { ...this.componentAccountAdministrator(3) },
        { ...this.componentNotaryInformation(4) }
      ]
    }
  }

  private async mounted () {
    // need to change call task api before

    this.task = await this.getTaskById(this.orgId)
    this.taskrRelationshipType = this.task.relationshipType
    await this.syncTaskUnderReview(this.task)

    this.isLoading = false
  }

  private async downloadAffidavit (): Promise<void> {
    // Invoke document service to get affidavit for current organization
    DocumentService.getSignedAffidavit(this.affidavitDocumentUrl, `${this.accountUnderReview.name}-affidavit`)
  }

  private openModal (isRejectModal:boolean = false, isConfirmationModal: boolean = false) {
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

    if (!this.isRejectModal) {
      await this.approveAccountUnderReview(this.task)
    } else {
      await this.rejectAccountUnderReview(this.task)
    }
    this.isSaving = false
    this.openModal(this.isRejectModal, true)
    // this.$router.push(Pages.STAFF_DASHBOARD)
  }

  private goBack (): void {
    this.$router.push(Pages.STAFF_DASHBOARD)
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
