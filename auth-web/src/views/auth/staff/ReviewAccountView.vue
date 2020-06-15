<template>
  <v-container>
    <v-btn
      large
      depressed
      color="default"
      class="primary--text"
    >
      <v-icon left class="mr-2">mdi-arrow-left</v-icon>
      <span>Back to Administration Home</span>
    </v-btn>
    <h1>Review Account</h1>
    <div class="my-2">Lorem ipsum dolor sit amet, consectetur adipiscing elit.</div>
      <v-card class="mt-8" flat>
      <v-row>
        <v-col class="main-col col-12 col-md-8">
          <div class="ma-3 px-8 px-md-12">

            <!-- Affidavit Section -->
            <v-row class="flex-column my-6">
              <h2 class="mb-5">1. Download Affidavit</h2>
              <div class="mb-5">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam at porttitor sem. Aliquam erat volutpat.</div>
              <v-btn large outlined color="primary" class="mb-5 mr-auto">
                <v-icon left class="mr-2">mdi-file-download-outline</v-icon>
                  <b>placeholder.jpg</b>
                </v-btn>
            </v-row>
            <v-divider/>

            <!-- Account Information Section -->
            <v-row class="flex-column my-6">
              <h2 class="mb-5">2. Account Information</h2>
              <v-col>
                <v-row>
                  <v-col class="col-12 col-md-3">
                    Account Name <br/> &amp; BC Online Details
                  </v-col>
                  <v-col>
                    <v-alert dark color="primary" class="py-4 pr-8 pl-4">
                      <div class="bcol-acc d-flex justify-space-between align-center">
                        <div>
                          <h2 class="white--text">{{ account.name }}</h2>
                          Account No: {{ account.bcolAccountDetails.accountNumber }} | Prime Contact ID: {{ account.bcolAccountDetails.userId }}
                        </div>
                      </div>
                    </v-alert>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col class="col-12 col-md-3">
                    Mailing Address
                  </v-col>
                  <v-col>
                    <div v-if="account.bcolAccountDetails.address">
                      {{ account.bcolAccountDetails.address.street }}<br/>
                      {{ account.bcolAccountDetails.address.city }}&nbsp;
                      {{ account.bcolAccountDetails.address.region }}&nbsp;
                      {{ account.bcolAccountDetails.address.postalCode }}<br/>
                      {{ account.bcolAccountDetails.address.country }}
                    </div>
                  </v-col>
                </v-row>
              </v-col>
            </v-row>
            <v-divider/>

            <!-- Account Administrator Section -->
            <v-row class="flex-column my-6">
              <h2 class="mb-5">3. Account Administrator</h2>
              <v-col>
                <v-row>
                  <v-col class="col-3">Given Name(s)</v-col>
                  <v-col>{{ accountAdmin.firstname }} {{ accountAdmin.lastname }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="col-3">Username</v-col>
                  <v-col>{{ accountAdmin.username }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="col-3">Email Address</v-col>
                  <v-col>{{ accountAdmin.emailAddress }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="col-3">Phone Number</v-col>
                  <v-col>{{ accountAdmin.phoneNumber }}</v-col>
                </v-row>
              </v-col>
            </v-row>
            <v-divider/>

            <!-- Notary Information Section -->
            <v-row class="flex-column my-6">
              <h2>4. Notary Information</h2>
              <v-col>
                <v-row>
                  <v-col class="col-3">Notary Name</v-col>
                  <v-col>{{ notary.name }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="col-3">Mailing Address</v-col>
                  <v-col>
                    <div v-if="notary.address">
                      {{ notary.address.street }}<br/>
                      {{ notary.address.city }}&nbsp;
                      {{ notary.address.region }}&nbsp;
                      {{ notary.address.postalCode }}<br/>
                      {{ notary.address.country }}
                    </div>
                    </v-col>
                </v-row>
                <v-row>
                  <v-col class="col-3">Email Address</v-col>
                  <v-col>{{ notary.emailAddress }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="col-3">Phone Number</v-col>
                  <v-col>{{ notary.phoneNumber }}</v-col>
                </v-row>
              </v-col>
            </v-row>
            <v-divider/>
            <v-row class="my-6">
              <v-col>
                <v-btn outlined color="success" class="mr-3">Approve</v-btn>
                <v-btn outlined color="red">Reject</v-btn>
              </v-col>
              <v-col class="d-flex justify-end">
                <v-btn depressed class="grey lighten-3"><b>DONE</b></v-btn>
              </v-col>
            </v-row>
          </div>
        </v-col>
        <v-col class="col-12 col-md-4">
          <div class="ma-3">
            <h2>Account Status</h2>
            <v-row>
              <v-col class="col-4">Status</v-col>
              <v-col></v-col>
            </v-row>
            <v-row>
              <v-col class="col-4">Approved By</v-col>
              <v-col></v-col>
            </v-row>
            <v-row>
              <v-col class="col-4">Created On</v-col>
              <v-col></v-col>
            </v-row>
          </div>
          </v-col>
      </v-row>
      </v-card>
  </v-container>
</template>

<script lang="ts">
import Component from 'vue-class-component'
import { Organization } from '@/models/Organization'
import { User } from '@/models/user'
import Vue from 'vue'

@Component({})
export default class ReviewAccountView extends Vue {
  // TODO - remove these stub objects and replace with actual data from store
  private account: Organization = {
    name: 'Account Four',
    bcolAccountDetails: {
      accountNumber: '180670',
      userId: 'PB25020',
      accountType: 'BCOL',
      address: {
        street: '1234 Some Street Name',
        city: 'Calgary',
        region: 'Alberta',
        postalCode: 'A1B 2C3',
        country: 'CANADA'
      }
    }
  }

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
}
</script>

<style lang="scss" scoped>
  .main-col {
    border-color: lightgray;
    border-right-style: solid;
    border-right-width: 1px;
  }
</style>
