<template>
  <v-container class="view-container">
    <v-row justify="center">
      <v-col cols="12" sm="6" class="text-center">
        <v-icon size="40" color="error" class="mb-6">mdi-lock-outline</v-icon>
        <h1>This account has been temporarily suspended</h1>
        <p class="mt-8 mb-10">Please contact the account administrator to reactivate this account.</p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">

import { Component, Mixins } from 'vue-property-decorator'
import AccountMixin from '@/components/auth/mixins/AccountMixin.vue'
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
}
</script>
