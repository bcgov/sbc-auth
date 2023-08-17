<template>
  <v-container>
    <v-row justify="center">
      <v-col
        cols="12"
        sm="6"
        class="text-center"
      >
        <v-icon
          size="42"
          color="grey darken-3"
          class="mb-6"
        >
          mdi-check
        </v-icon>
        <h1 class="mb-5">
          {{ $t('extraProdOrgSuccessTitle') }}
        </h1>
        <p class="mb-9">
          {{ $t('pendingAffidvitReviewMessage', descriptionParams) }}
        </p>
        <div>
          <v-btn
            large
            color="primary"
            @click="goTo('home')"
          >
            <strong>BC Registries Home</strong>
          </v-btn>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
import { Organization } from '@/models/Organization'
import { Pages } from '@/util/constants'
import Vue from 'vue'
import { mapState } from 'vuex'

@Component({
  computed: {
    ...mapState('org', ['currentOrganization'])
  }
})
export default class NonBcscAccountCreationSuccessView extends Vue {
  protected readonly currentOrganization!: Organization
  private readonly descriptionParams: any = { 'days': ConfigHelper.getAccountApprovalSlaInDays() }

  private goTo (page) {
    switch (page) {
      case 'home': this.$router.push('/')
        break
      case 'team-members': this.$router.push(`/${Pages.MAIN}/${this.currentOrganization.id}/settings/team-members`)
        break
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";

  .container {
    padding-top: 3rem;
    padding-bottom: 3rem;
  }
</style>
