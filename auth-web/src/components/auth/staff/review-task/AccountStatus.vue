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

<style lang="scss" scoped>
  // BC Online Account Information
  .bcol-acc__name {
    font-size: 1.125rem;
    font-weight: 700;
  }

  .bcol-acc__meta {
    margin: 0;
    padding: 0;
    list-style-type: none;
    font-size: .925rem;

    li {
      position: relative;
      display: inline-block
    }

    li + li {
      &:before {
        content: ' | ';
        display: inline-block;
        position: relative;
        top: -2px;
        left: 2px;
        width: 2rem;
        vertical-align: top;
        text-align: center;
      }
    }
  }

  .mailing-address {
    list-style-type: none;
    margin: 0;
    padding: 0;
  }

  // .select-button {
  //   width: 8.75rem;
  // }

  // .crumbs a {
  //   font-size: 0.875rem;
  //   text-decoration: none;

  //   i {
  //     margin-top: -2px;
  //   }
  // }

  // .crumbs a:hover {
  //   span {
  //     text-decoration: underline;
  //   }
  // }
</style>
