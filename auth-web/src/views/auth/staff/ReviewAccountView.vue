<template>
  <v-container class="view-container pt-0">

    <!-- Breadcrumbs / Back Navigation -->
    <nav class="crumbs">
      <div class="pt-5 pb-3">
        <v-btn large text color="primary" class="back-btn pr-2 pl-1">
          <v-icon small class="mr-1">mdi-arrow-left</v-icon>
          <span>Back to Staff Dashboard</span>
        </v-btn>
      </div>
    </nav>

    <div class="view-header flex-column">
      <h1 class="view-header__title">Review Account</h1>
      <p class="mt-2 mb-0">Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
    </div>
    <v-card class="mt-8" flat v-if="!isLoading">
      <v-row class="mr-0 ml-0">

        <!-- Account Information Column -->
        <v-col class="main-col col-12 col-md-8 pa-6 pa-md-8">

            <!-- Affidavit Section -->
            <section>
              <h2 class="mb-7">1. Download Affidavit</h2>
              <p class="mb-9">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam at porttitor sem. Aliquam erat volutpat.</p>
              <v-btn x-large="" outlined color="primary" class="font-weight-bold" @click="downloadAffidavit()">
                <v-icon left class="mr-2">mdi-file-download-outline</v-icon>
                placeholder.jpg
              </v-btn>
            </section>

            <v-divider class="mt-10 mb-8"></v-divider>

            <section>
              <h2 class="mb-3">2. Account Information</h2>
              <v-row>
                <v-col class="col-12 col-sm-3">
                  Account Name <br/> &amp; BC Online Details
                </v-col>
                <v-col>
                  <v-alert dark color="primary" class="bcol-acc mb-0 px-7 py-5">
                    <div class="bcol-acc__name mt-n1">
                      {{ accountUnderReview.name }}
                    </div>
                    <ul class="bcol-acc__meta">
                      <li>
                        Account No: {{ accountUnderReview.bcolAccountDetails.accountNumber }}
                      </li>
                      <li>
                        Prime Contact ID: {{ accountUnderReview.bcolAccountDetails.userId }}
                      </li>
                    </ul>
                  </v-alert>
                </v-col>
              </v-row>
              <v-row v-if="acaccountUnderReviewcount.bcolAccountDetails.address">
                <v-col class="col-12 col-sm-3">
                  Mailing Address
                </v-col>
                <v-col>
                  <ul class="mailing-address">
                    <li>{{ accountUnderReview.bcolAccountDetails.address.street }}</li>
                    <li>{{ accountUnderReview.bcolAccountDetails.address.city }} {{ accountUnderReview.bcolAccountDetails.address.region }} {{ accountUnderReview.bcolAccountDetails.address.postalCode }}</li>
                    <li>{{ accountUnderReview.bcolAccountDetails.address.country }}</li>
                  </ul>
                </v-col>
              </v-row>
            </section>

            <v-divider class="mt-5 mb-8"></v-divider>

            <!-- Account Administrator Section -->
            <section>
              <h2 class="mb-5">3. Account Administrator</h2>
              <v-row>
                <v-col class="cols-12 col-sm-3 py-2">Given Name(s)</v-col>
                <v-col class="py-2">{{ accountAdmin.firstname }} {{ accountAdmin.lastname }}</v-col>
              </v-row>
              <v-row>
                <v-col class="cols-12 col-sm-3 py-2">Username</v-col>
                <v-col class="py-2">{{ accountAdmin.username }}</v-col>
              </v-row>
              <v-row>
                <v-col class="cols-12 col-sm-3 py-2">Email Address</v-col>
                <v-col class="py-2">{{ accountAdmin.emailAddress }}</v-col>
              </v-row>
              <v-row>
                <v-col class="cols-12 col-sm-3 py-2">Phone Number</v-col>
                <v-col class="py-2">{{ accountAdmin.phoneNumber }}</v-col>
              </v-row>
            </section>

            <v-divider class="mt-7 mb-8"></v-divider>

            <!-- Notary Information Section -->
            <section>
              <h2 class="mb-5">4. Notary Information</h2>
              <v-row>
                  <v-col class="cols-12 col-sm-3 py-2">Notary Name</v-col>
                  <v-col class="py-2">{{ notary.name }}</v-col>
                </v-row>
                <v-row v-if="notary.address">
                  <v-col class="cols-12 col-sm-3 py-2">Mailing Address</v-col>
                  <v-col class="py-2">
                    <div>
                      <ul class="mailing-address">
                        <li>{{ notary.address.street }}</li>
                        <li>{{ notary.address.city }} {{ notary.address.region }} {{ notary.address.postalCode }}</li>
                        <li>{{ notary.address.country }}</li>
                      </ul>
                    </div>
                    </v-col>
                </v-row>
                <v-row>
                  <v-col class="cols-12 col-sm-3 py-2">Email Address</v-col>
                  <v-col class="py-2">{{ notary.emailAddress }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="cols-12 col-sm-3 py-2">Phone Number</v-col>
                  <v-col class="py-2">{{ notary.phoneNumber }}</v-col>
                </v-row>
            </section>

            <v-divider class="mt-8 mb-6"></v-divider>

            <v-row class="form__btns">
              <v-col class="pb-0">
                <v-btn large outlined color="success" class="font-weight-bold mr-2">Approve</v-btn>
                <v-btn large outlined color="red" class="font-weight-bold">Reject</v-btn>
              </v-col>
              <v-col class="pb-0 text-right">
                <v-btn large depressed class="grey lighten-3 font-weight-bold">DONE</v-btn>
              </v-col>
            </v-row>

        </v-col>

        <!-- Account Status Column -->
        <v-col class="col-12 col-md-4 pa-6 pa-md-8">
          <h2 class="mb-5">Account Status</h2>
          <v-row>
            <v-col class="col-12 col-sm-5 py-2">Status</v-col>
            <v-col class="py-2"></v-col>
          </v-row>
          <v-row>
            <v-col class="col-12 col-sm-5 py-2">Approved By</v-col>
            <v-col class="py-2"></v-col>
          </v-row>
          <v-row>
            <v-col class="col-12 col-sm-5 py-2">Created On</v-col>
            <v-col class="py-2"></v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import Component from 'vue-class-component'
import DocumentService from '@/services/document.services'
import OrgService from '@/services/org.services'
import { Organization } from '@/models/Organization'
import { Prop } from 'vue-property-decorator'
import { User } from '@/models/user'
import Vue from 'vue'

@Component({})
export default class ReviewAccountView extends Vue {
  @Prop() orgId: number
  private isLoading: boolean = true
  private accountUnderReview: Organization

  // TODO - remove these stub objects and replace with actual data from store
  // private account: Organization = {
  //   name: 'Account Four',
  //   bcolAccountDetails: {
  //     accountNumber: '180670',
  //     userId: 'PB25020',
  //     accountType: 'BCOL',
  //     address: {
  //       street: '1234 Some Street Name',
  //       city: 'Calgary',
  //       region: 'Alberta',
  //       postalCode: 'A1B 2C3',
  //       country: 'CANADA'
  //     }
  //   }
  // }

  private accountAdmin: User = {
    firstname: 'John',
    lastname: 'Smith',
    username: 'jsmith'
  }

  private notary = {
    name: 'Notary Name',
    emailAddress: 'email@email.com',
    phoneNumber: '(555) 555-5555',
    address: {
      street: '1234 Some Street Name',
      city: 'Calgary',
      region: 'Alberta',
      postalCode: 'A1B 2C3',
      country: 'CANADA'
    }
  }

  private async mounted () {
    this.accountUnderReview = (await OrgService.getOrganization(this.orgId))?.data
    this.isLoading = false
  }

  private async downloadAffidavit (): Promise<void> {
    // Invoke document service to get affidavit for current organization
  }
}
</script>

<style lang="scss" scoped>
  .main-col {
    border-color: lightgray;
    border-right-style: solid;
    border-right-width: 1px;
  }

  // BC Online Account Information
  .bcol-acc__name {
    font-size: 1.125rem;
    font-weight: 700;
  }

  .bcol-acc__meta {
    margin: 0;
    padding: 0;
    list-style-type: none;

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
