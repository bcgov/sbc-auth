<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" lg="8" class="text-center">
        <v-icon size="48" color="error" class="mb-6">mdi-lock-outline</v-icon>
        <h1 class="mb-5">Not Authorized</h1>
        <p class="mb-9">{{ errorMessage }}</p>
        <v-btn large link color="primary" href="./">Go to Homepage</v-btn>
        <v-btn large outlined link color="primary" class="ml-1" href="mailto:SBC_ITOperationsSupport@gov.bc.ca?subject=BC Registries Application Support Request"
          v-if="isStaff">Contact Support</v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component } from 'vue-property-decorator'
import { Role } from '@/util/constants'
import { UserInfo } from 'sbc-common-components/src/models/userInfo'
import Vue from 'vue'
import { mapState } from 'vuex'

@Component({
  computed: {
    ...mapState('user', ['currentUser'])
  }
})
export default class UnauthorizedView extends Vue {
  readonly currentUser!: UserInfo
  errorMessage : string = ''
  isStaff: boolean = false

  mounted () {
    this.isStaff = this.currentUser && this.currentUser.roles.includes(Role.Staff)
    this.errorMessage = this.isStaff
      ? this.$t('staffUnauthorizedMsg').toString()
      : this.$t('clientUnauthorizedMsg').toString()
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
