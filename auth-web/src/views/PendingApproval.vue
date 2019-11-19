<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" lg="8" class="text-center">
        <v-icon size="48" color="primary" class="mb-6">mdi-information-outline</v-icon>
        <div v-if="$route.params.team_name">
          <h1 class="mb-5">Thanks for joining the team {{ $route.params.team_name }} at BC Registries & Online Services.</h1>
          <p class="mb-9">{{ $t('pendingInvitationMsg')}}</p>
        </div>
        <div>
          <h1 class="mb-7">{{ $t('noPendingInvitationTitle')}}</h1>
          <p class="mb-9">{{ $t('noPendingInvitationMsg')}}</p>
        </div>
        <v-btn large link color="primary" href="../">{{ $t('homeBtnLabel')}}</v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component } from 'vue-property-decorator'
import { Role } from '@/util/constants'
import { UserInfo } from '@/models/userInfo'
import Vue from 'vue'
import { mapState } from 'vuex'

  @Component({})
export default class Unauthorized extends Vue {
  mounted () {
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
