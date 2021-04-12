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
          <router-link :to="accountUnderReview.statusCode === accountStatusEnum.REJECTED ? pagesEnum.STAFF_DASHBOARD_REJECTED: pagesEnum.STAFF_DASHBOARD_REVIEW">
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
            <template v-for="(component, idx) in componentList">
              <component
                :key="component.id"
                :is="component.component"
                v-bind="component.props"
                v-on="component.events"
              />
              <v-divider class="mt-11 mb-8" :key="`divider-${component.id}`" v-if="componentList.length-1 !== idx"></v-divider>
            </template>
          </v-col>

          <!-- Account Status Column -->
          <v-col class="col-12 col-md-4 pl-0 pt-8 pr-8 d-flex">
            <v-divider vertical class="mb-4 mr-8"></v-divider>
            <div class="flex-grow-1">
            <AccountStatusTab
              :accountUnderReview="accountUnderReview"
              :accountUnderReviewAffidavitInfo="accountUnderReviewAffidavitInfo"
              :isPendingReviewPage="isPendingReviewPage"
            />
            </div>
          </v-col>
        </v-row>

        <v-container v-if="canSelect" class="pa-8 pt-0">
          <v-divider class="mb-10"></v-divider>
          <div class="form-btns d-flex justify-space-between">
            <div>
              <v-btn large :outlined="!approveSelected" color="success" class="font-weight-bold mr-2 select-button" @click="selectApprove()">
                <v-icon left class="mr-3" v-if="approveSelected">mdi-check</v-icon>
                <span>{{approveSelected ? 'Approved' : 'Approve'}}</span>
              </v-btn>
              <v-btn large :outlined="!rejectSelected" color="red" class="font-weight-bold white--text select-button" @click="selectReject()">
                <v-icon left class="mr-3" v-if="rejectSelected">mdi-close</v-icon>
                <span>{{rejectSelected ? 'Rejected' : 'Reject'}}</span>
              </v-btn>
            </div>
            <div>
              <v-btn large color="primary" class="font-weight-bold mr-2" :loading="isSaving" :disabled="!approveSelected && !rejectSelected" @click="saveSelection()">Save and exit</v-btn>
              <v-btn large depressed :to=pagesEnum.STAFF_DASHBOARD>Cancel</v-btn>
            </div>
          </div>
        </v-container>

      </v-card>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Account, AccountStatus, Pages } from '@/util/constants'
import { MembershipType, Organization } from '@/models/Organization'
import { mapActions, mapGetters, mapState } from 'vuex'
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

// import OrgService from '@/services/org.services'
import { Prop } from 'vue-property-decorator'
import StaffModule from '@/store/modules/staff'
import { User } from '@/models/user'
import Vue from 'vue'
import { getModule } from 'vuex-module-decorators'
// import moment from 'moment'

@Component({
  components: {
    DownloadAffidavit,
    AccountInformation,
    AccountAdministrator,
    NotaryInformation,
    AccountStatusTab
  },
  computed: {
    ...mapState('staff', ['accountUnderReview', 'accountUnderReviewAddress', 'accountUnderReviewAdmin', 'accountUnderReviewAdminContact', 'accountUnderReviewAffidavitInfo']),
    ...mapGetters('staff', ['accountNotaryName', 'accountNotaryContact', 'affidavitDocumentUrl'])
  },
  methods: {
    ...mapActions('staff', ['syncAccountUnderReview', 'approveAccountUnderReview', 'rejectAccountUnderReview'])
  }
})
export default class ReviewAccountView extends Vue {
  @Prop() orgId: number
  private staffStore = getModule(StaffModule, this.$store)
  private isLoading = true
  private isSaving = false
  private approveSelected = false
  private rejectSelected = false
  private readonly accountUnderReview!: Organization
  private readonly accountUnderReviewAddress!: Address
  private readonly accountUnderReviewAdmin!: User
  private readonly accountUnderReviewAdminContact!: Contact
  private readonly accountUnderReviewAffidavitInfo!: AffidavitInformation
  private readonly accountNotaryName!: string
  private readonly accountNotaryContact!: Contact
  private readonly affidavitDocumentUrl!: string
  private readonly syncAccountUnderReview!: (organizationIdentifier: number) => Promise<void>
  private readonly approveAccountUnderReview!: () => Promise<void>
  private readonly rejectAccountUnderReview!: () => Promise<void>
  private readonly pagesEnum = Pages
  private readonly accountStatusEnum = AccountStatus

  private get canSelect (): boolean {
    return this.accountUnderReview.statusCode === AccountStatus.PENDING_STAFF_REVIEW
  }

  private get statusLabel (): string {
    switch (this.accountUnderReview.statusCode) {
      case AccountStatus.ACTIVE:
        return 'Approved'
      case AccountStatus.REJECTED:
        return 'Rejected'
      case AccountStatus.PENDING_STAFF_REVIEW:
        return 'Pending'
      default:
        return ''
    }
  }

  private get isPendingReviewPage () {
    return this.accountUnderReview?.statusCode === AccountStatus.PENDING_STAFF_REVIEW
  }

  get componentList () {
    return [{
      id: 'DownloadAffidavit',
      component: DownloadAffidavit,
      props: {
        tabNumber: 1,
        title: 'Download Affidavit',
        subTitle: 'Download the notarized affidavit associated with this account to verify the account creators identity and associated information.',
        affidavitName: this.accountUnderReview.name
      },
      events: { 'emit-download-affidavit': this.downloadAffidavit }

    },
    {
      id: 'AccountInformation',
      component: AccountInformation,
      props: {
        tabNumber: 2,
        title: 'Account Information',
        accountUnderReview: this.accountUnderReview,
        accountUnderReviewAddress: this.accountUnderReviewAddress
      }
    },
    {
      id: 'AccountAdministrator',
      component: AccountAdministrator,
      props: {
        tabNumber: 3,
        title: 'Account Administrator',
        accountUnderReviewAdmin: this.accountUnderReviewAdmin,
        accountUnderReviewAdminContact: this.accountUnderReviewAdminContact
      }
    },
    {
      id: 'NotaryInformation',
      component: NotaryInformation,
      props: {
        tabNumber: 4,
        title: 'Notary Information',
        accountNotaryContact: this.accountNotaryContact,
        accountNotaryName: this.accountNotaryName
      }
    }

    ]
  }
  // needed for product approval
  //  {
  //     id: 'AgreementInformation',
  //     component: AgreementInformation,
  //     props: {
  //       tabNumber: 5,
  //       title: 'Agreement',
  //       isTOSAlreadyAccepted: true,
  //       orgName: this.accountUnderReview.name,
  //       userName: `${this.accountUnderReviewAdmin.firstname} ${this.accountUnderReviewAdmin.lastname}`
  //     }
  //   }

  // private formatDate (date: Date): string {
  //   return moment(date).format('MMM DD, YYYY')
  // }

  private async mounted () {
    await this.syncAccountUnderReview(this.orgId)

    // Set initial approved/rejected status based on current account
    switch (this.accountUnderReview.statusCode) {
      case AccountStatus.ACTIVE:
        this.approveSelected = true
        break
      case AccountStatus.REJECTED:
        this.rejectSelected = true
        break
      default:
        break
    }

    this.isLoading = false
  }

  private async downloadAffidavit (): Promise<void> {
    // Invoke document service to get affidavit for current organization
    DocumentService.getSignedAffidavit(this.affidavitDocumentUrl, `${this.accountUnderReview.name}-affidavit`)
  }

  private selectApprove (): void {
    if (this.canSelect) {
      this.approveSelected = true
      this.rejectSelected = false
    }
  }

  private selectReject (): void {
    if (this.canSelect) {
      this.approveSelected = false
      this.rejectSelected = true
    }
  }

  private async saveSelection (): Promise<void> {
    this.isSaving = true
    if (this.approveSelected) {
      await this.approveAccountUnderReview()
    } else if (this.rejectSelected) {
      await this.rejectAccountUnderReview()
    }
    this.$router.push(Pages.STAFF_DASHBOARD)
  }

  private goBack (): void {
    this.$router.push(Pages.STAFF_DASHBOARD)
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
