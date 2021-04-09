<template>
  <div>
    <h2 class="mb-5">{{`${tabNumber !==null ?  `${tabNumber}.` : ''} ${title}`}}</h2>
    <v-row>
      <v-col class="col-12 col-sm-5 py-2">Status</v-col>
      <v-col class="py-2">{{ statusLabel }}</v-col>
    </v-row>
    <v-row v-if="!isPendingReviewPage">
      <v-col class="col-12 col-sm-5 py-2">
        <span v-if="accountUnderReview.statusCode === 'ACTIVE'">Approved By</span>
        <span v-if="accountUnderReview.statusCode === 'REJECTED'">Rejected By</span>
      </v-col>
      <v-col class="py-2">
        {{ accountUnderReviewAffidavitInfo.decisionMadeBy }}<br/>
        {{ formatDate(accountUnderReviewAffidavitInfo.decisionMadeOn) }}
      </v-col>
    </v-row>
    <v-row>
      <v-col class="col-12 col-sm-5 py-2">Created On</v-col>
      <v-col class="py-2">{{ formatDate(accountUnderReview.created) }}</v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { AccountStatus } from '@/util/constants'
import { AffidavitInformation } from '@/models/affidavit'
import { Organization } from '@/models/Organization'
import moment from 'moment'

@Component({})
export default class AccountStatusTab extends Vue {
  @Prop({ default: null }) private tabNumber: number
  @Prop({ default: false }) private isPendingReviewPage: boolean
  @Prop({ default: 'Account Status' }) private title: string
  @Prop({ default: {} }) accountUnderReview: Organization
  @Prop({ default: {} }) accountUnderReviewAffidavitInfo: AffidavitInformation

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
  private formatDate (date: Date): string {
    return moment(date).format('MMM DD, YYYY')
  }
}
</script>
