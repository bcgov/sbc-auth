<template>
  <v-container class="unauthorized-view text-center">
    <v-icon x-large class="mb-6">mdi-lock</v-icon>
    <h1 class="mb-7" v-if="$route.params.team_name">Thanks for joining the team {{ $route.params.team_name }} at BC Registries & Online Services.</h1>
    <h3 class="mb-7">The administrator for this team needs to verify your invitation before you can access this application.</h3>
    <v-btn large depressed link color="primary" href="../">Go to Homepage</v-btn>
    <v-btn large outlined link color="primary"
           href="mailto:SBC_ITOperationsSupport@gov.bc.ca?subject=BC Registries Application Support Request"
           v-if="isStaff">Contact Support
    </v-btn>
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
  .v-btn + .v-btn {
    margin-left: 0.5rem;
  }
</style>
