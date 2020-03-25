<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" lg="8" class="text-center">
        <v-icon size="48" color="error" class="mb-6">{{(isDirSearchUser) ? 'mdi-information-outline' : 'mdi-lock-outline'}}</v-icon>
        <h1 class="mb-5">Not Authorized</h1>
        <p class="mb-9">{{ errorMessage }}</p>
        <div v-if="isDirSearchUser">
          <v-btn
            large
            color="primary"
            @click="navigate('termsofuse')"
          >
            Terms of Use
          </v-btn>
          <v-btn
            large
            color="primary"
            class="ml-6"
            @click="navigate('logout')"
          >
            Log out
          </v-btn>
        </div>
        <template v-else>
          <v-btn large link color="primary" href="./">Go to Homepage</v-btn>
          <v-btn large outlined link color="primary" class="ml-1" href="mailto:SBC_ITOperationsSupport@gov.bc.ca?subject=BC Registries Application Support Request"
            v-if="isStaff">Contact Support</v-btn>
        </template>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { IdpHint, LoginSource, Role } from '@/util/constants'
import { Component } from 'vue-property-decorator'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import Vue from 'vue'
import { mapState } from 'vuex'

@Component({
  computed: {
    ...mapState('user', ['currentUser'])
  }
})
export default class UnauthorizedView extends Vue {
  readonly currentUser!: KCUserProfile
  errorMessage : string = ''
  isStaff: boolean = false
  isDirSearchUser: boolean = false

  beforeMount () {
    // TODO: Replace the login source check with whatever value for director search account.
    this.isDirSearchUser = (this.currentUser?.loginSource === LoginSource.BCROS)
  }

  mounted () {
    this.isStaff = this.currentUser && this.currentUser.roles.includes(Role.Staff)
    this.errorMessage = this.isStaff
      ? this.$t('staffUnauthorizedMsg').toString()
      : this.$t('clientUnauthorizedMsg').toString()
    this.errorMessage = this.isDirSearchUser ? this.$t('dirSearchUnauthorizedMsg').toString() : this.errorMessage
  }

  navigate (page) {
    switch (page) {
      case 'termsofuse': this.$router.push(`/userprofileterms`)
        break
      case 'logout': this.$router.push(`/signout`)
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
