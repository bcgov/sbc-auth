<template>
  <v-container class="view-container">
    <v-row justify="center">
      <v-col cols="12" sm="6" class="text-center">
        <v-icon size="40" color="error" class="mb-6">mdi-alert-circle-outline</v-icon>
        <h1>Your Account is Temporarily Suspended</h1>
        <p class="mt-8 mb-10">Your account is temporarily suspended from <strong>{{suspendedDate}}</strong>. <br />
        Please contact the account administrator to reactivate your account</p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">

import { Component, Mixins } from 'vue-property-decorator'
import AccountMixin from '@/components/auth/mixins/AccountMixin.vue'
import CommonUtils from '@/util/common-util'
import { Organization } from '@/models/Organization'
import { Pages } from '@/util/constants'
import Vue from 'vue'
import { mapState } from 'vuex'

@Component({
  computed: {
    ...mapState('org', ['currentOrganization'])
  }
})
export default class AccountCreationSuccessView extends Mixins(AccountMixin) {
  protected readonly currentOrganization!: Organization
  private formatDate = CommonUtils.formatDisplayDate

  private get suspendedDate () {
    return (this.currentOrganization?.suspendedOn) ? this.formatDate(new Date(this.currentOrganization.suspendedOn)) : ''
  }
}
</script>
