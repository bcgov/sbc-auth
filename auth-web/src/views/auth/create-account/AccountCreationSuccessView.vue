<template>
  <v-container
    class="view-container"
    data-test="div-account-setup-success-container"
  >
    <template v-if="redirectToUrl">
      <v-row justify="center">
        <v-col
          cols="12"
          class="text-center"
        >
          <v-progress-circular
            indeterminate
            color="primary"
          />
        </v-col>
      </v-row>
    </template>
    <v-row
      v-else
      justify="center"
    >
      <v-col
        cols="12"
        sm="6"
        class="text-center"
      >
        <v-icon
          size="48"
          color="primary"
          class="mb-6"
        >
          mdi-check
        </v-icon>
        <h1>{{ $t('bcscAccountCreationSuccessTitle') }}</h1>
        <p class="mt-8 mb-5">
          {{ $t('bcscAccountCreationSuccessSubtext1') }}
        </p>
        <p class="mb-10">
          {{ $t('bcscAccountCreationSuccessSubtext2') }}
        </p>
        <div class="btns">
          <v-btn
            large
            color="primary"
            class="action-btn font-weight-bold"
            data-test="btn-goto-home"
            @click="goTo('home')"
          >
            Home
          </v-btn>
          <span class="mx-3">or</span>
          <v-btn
            v-if="isRegularAccount"
            large
            color="primary"
            class="action-btn font-weight-bold"
            data-test="btn-setup-team"
            @click="goTo('setup-team')"
          >
            Set up team
          </v-btn>
          <v-btn
            v-if="!isRegularAccount"
            large
            color="primary"
            class="action-btn font-weight-bold"
            data-test="btn-add-team-members"
            @click="goTo('team-members')"
          >
            Add Team Members
          </v-btn>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">

import { Component, Mixins, Prop } from 'vue-property-decorator'
import AccountMixin from '@/components/auth/mixins/AccountMixin.vue'
import ConfigHelper from '@/util/config-helper'
import { Pages } from '@/util/constants'
import { mapState } from 'pinia'
import { useOrgStore } from '@/stores/org'

@Component({
  computed: {
    ...mapState(useOrgStore, ['currentOrganization'])
  }
})
export default class AccountCreationSuccessView extends Mixins(AccountMixin) {
  @Prop({ default: '' }) redirectToUrl: string

  mounted () {
    // redirectToUrl is only ever present when this screen is reached via a flow (like
    // vendor-linking) that needs to resume elsewhere after account creation — every other
    // caller leaves it unset.
    if (this.redirectToUrl) {
      this.$router.push(this.redirectToUrl)
    }
  }

  goTo (page) {
    switch (page) {
      case 'home': window.location.assign(`${ConfigHelper.getRegistryHomeURL()}dashboard/?accountid=${this.currentOrganization.id}`)
        break
      case 'team-members': this.$router.push(`/${Pages.MAIN}/${this.currentOrganization.id}/settings/team-members`)
        break
      case 'setup-team': this.$router.push(`account-login-options-info`)
        break
    }
  }
}
</script>

<style lang="scss" scoped>
  .action-btn {
    width: 8rem;
  }
</style>
