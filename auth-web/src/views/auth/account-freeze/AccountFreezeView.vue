<template>
  <v-container class="view-container" v-if="isAccountStatusNsfSuspended">
    <v-row justify="center">
      <v-col cols="12" sm="6" class="text-center">
        <v-icon size="40" color="error" class="mb-6">mdi-alert-circle-outline</v-icon>
        <h1>Your Account is Temporarily Suspended</h1>
        <p class="mt-8 mb-10">Your account is temporarily suspended from <strong>{{suspendedDate}}</strong>. <br />
        Please contact the account administrator to reactivate your account</p>
      </v-col>
    </v-row>
  </v-container>
  <v-container class="view-container" v-else>
    <AccountSuspendedView ></AccountSuspendedView>
  </v-container>
</template>

<script lang="ts">

import AccountMixin from '@/components/auth/mixins/AccountMixin.vue'
import CommonUtils from '@/util/common-util'
import { AccountStatus } from '@/util/constants'
import { Component, Mixins } from 'vue-property-decorator'
import { mapState } from 'vuex'
import AccountSuspendedView from './AccountSuspendedView.vue'

@Component({
  components: {
    AccountSuspendedView
  },
  computed: {
    ...mapState('org', ['currentOrganization'])
  }
})
export default class AccountCreationSuccessView extends Mixins(AccountMixin) {
  private formatDate = CommonUtils.formatDisplayDate

  private get isAccountStatusNsfSuspended () : boolean {
    return this.currentOrganization?.accountStatus === AccountStatus.NSF_SUSPENDED
  }

  private get suspendedDate () {
    return (this.currentOrganization?.suspendedOn) ? this.formatDate(new Date(this.currentOrganization.suspendedOn)) : ''
  }
}
</script>
