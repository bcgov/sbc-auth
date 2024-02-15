<template>
  <v-container
    class="view-container"
    data-test="div-account-setup-success-container"
  >
    <v-row justify="center">
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
import AccountMixin from '@/components/auth/mixins/AccountMixin.vue'
import ConfigHelper from '@/util/config-helper'
import { Pages } from '@/util/constants'
import { defineComponent } from '@vue/composition-api'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  name: 'AccountCreationSuccessView',
  mixins: [AccountMixin],
  setup (props, { root }) {
    const orgStore = useOrgStore()
    function goTo (page) {
      switch (page) {
        case 'home': window.location.assign(`${ConfigHelper.getRegistryHomeURL()}dashboard/?accountid=${orgStore.currentOrganization.id}`)
          break
        case 'team-members': root.$router.push(`/${Pages.MAIN}/${orgStore.currentOrganization.id}/settings/team-members`)
          break
        case 'setup-team': root.$router.push(`account-login-options-info`)
          break
      }
    }
    return {
      goTo
    }
  }
})
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";

  .action-btn {
    width: 8rem;
  }
</style>
