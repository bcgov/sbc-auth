<template>
  <v-container class="unauthorized-view text-center">
    <v-icon x-large class="mb-6">mdi-lock</v-icon>
    <h1 class="mb-7">Not Authorized</h1>
    <p class="mb-9">{{ errorMessage }}</p>
    <v-btn large depressed link color="primary" href="./">Go to Homepage</v-btn>
    <v-btn large outlined link color="primary" href="mailto:SBC_ITOperationsSupport@gov.bc.ca?subject=BC Registries Application Support Request"
      v-if="isStaff">Contact Support</v-btn>
  </v-container>
</template>

<script lang="ts">
import { Component } from 'vue-property-decorator'
import { Role } from '@/util/constants'
import { UserInfo } from '@/models/userInfo'
import Vue from 'vue'
import { mapState } from 'vuex'

@Component({
  computed: {
    ...mapState('user', ['currentUser'])
  }
})
export default class Unauthorized extends Vue {
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
  .v-btn + .v-btn {
    margin-left: 0.5rem;
  }
</style>
