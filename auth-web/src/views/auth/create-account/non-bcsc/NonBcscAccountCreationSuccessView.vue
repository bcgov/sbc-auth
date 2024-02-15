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
import ConfigHelper from '@/util/config-helper'
import { Pages } from '@/util/constants'
import { defineComponent } from '@vue/composition-api'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  name: 'ExtraProdOrgSuccessView',
  setup (props, { root }) {
    const descriptionParams = { 'days': ConfigHelper.getAccountApprovalSlaInDays() }
    const orgStore = useOrgStore()

    function goTo (page) {
      switch (page) {
        case 'home': root.$router.push('/')
          break
        case 'team-members': root.$router.push(`/${Pages.MAIN}/${orgStore.currentOrganization.id}/settings/team-members`)
          break
      }
    }

    return {
      descriptionParams,
      goTo
    }
  }
})
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";

  .container {
    padding-top: 3rem;
    padding-bottom: 3rem;
  }
</style>
