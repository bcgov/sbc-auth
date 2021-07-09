<template>
  <section>
    <h2 class="mb-3">{{`${tabNumber !== null ?  `${tabNumber}. ` : ''}${title}`}}</h2>
    <v-row v-if="accountUnderReview.orgType === Account.BASIC">
      <v-col class="col-12 col-sm-3">
        Account Name
      </v-col>
      <v-col>
        {{ accountUnderReview.name }}
      </v-col>
    </v-row>
    <!-- for GOVM account showing banch name  -->
     <v-row v-else-if="accountUnderReview.orgType === Account.PREMIUM && accountUnderReview.accessType === AccessType.GOVM">
      <v-col class="col-12 col-sm-3">
       <span> Account Name <br/> &amp; Branch Details</span>
      </v-col>
      <v-col>
        <v-alert dark color="primary" class="bcol-acc mb-0 px-7 py-5">
          <div class="bcol-acc__name mt-n1">
            {{ accountUnderReview.name }}
          </div>
          <ul class="bcol-acc__meta">
            <li>
              Branch Name : {{ accountUnderReview.branchName }}
            </li>
          </ul>
        </v-alert>
      </v-col>
    </v-row>
    <!-- all other accounts -->
    <v-row v-else>
      <v-col class="col-12 col-sm-3">
        <span>Account Name <br/> &amp; BC Online Details</span>
      </v-col>
      <v-col>
        <v-alert dark color="primary" class="bcol-acc mb-0 px-7 py-5">
          <div class="bcol-acc__name mt-n1">
            {{ accountUnderReview.name }}
          </div>
          <ul class="bcol-acc__meta" v-if="accountUnderReview.bcolAccountId">
            <li>
              Account No: {{ accountUnderReview.bcolAccountId }}
            </li>
            <li>
              Prime Contact ID: {{ accountUnderReview.bcolUserId }}
            </li>
          </ul>
        </v-alert>
      </v-col>
    </v-row>
    <v-row v-if="accountUnderReviewAddress">
      <v-col class="col-12 col-sm-3">
        Mailing Address
      </v-col>
      <v-col>
        <ul class="mailing-address">
          <li>{{ accountUnderReviewAddress.street }}</li>
          <li>{{ accountUnderReviewAddress.city }} {{ accountUnderReviewAddress.region }} {{ accountUnderReviewAddress.postalCode }}</li>
          <li>{{ accountUnderReviewAddress.country }}</li>
        </ul>
      </v-col>
    </v-row>
  </section>
</template>

<script lang="ts">
import { AccessType, Account } from '@/util/constants'
import { Component, Prop, Vue } from 'vue-property-decorator'
import { Address } from '@/models/address'

@Component({})
export default class AccountInformation extends Vue {
  // @Prop({ default: 'BASIC' }) private orgType: string
  @Prop({ default: null }) private tabNumber: number

  @Prop({ default: 'Account Information' }) private title: string
  @Prop({ default: {} }) accountUnderReview: any
  @Prop({ default: null }) accountUnderReviewAddress: Address

  AccessType = AccessType
  Account = Account
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

</style>
