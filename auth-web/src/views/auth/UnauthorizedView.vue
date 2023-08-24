<template>
  <v-container class="view-container">
    <v-row justify="center">
      <v-col
        cols="12"
        lg="8"
        class="text-center"
      >
        <v-icon
          size="48"
          color="error"
          class="mb-6"
        >
          mdi-lock-outline
        </v-icon>
        <h1>{{ $t('notAuthorized') }}</h1>
        <p class="mt-8 mb-10">
          {{ errorMessage }}
        </p>
        <div class="btns">
          <v-btn
            large
            link
            color="primary"
            href="./"
          >
            Go to Homepage
          </v-btn>
          <v-btn
            v-if="isStaff"
            large
            outlined
            link
            color="primary"
            class="ml-1"
            href="mailto:SBC_ITOperationsSupport@gov.bc.ca?subject=BC Registries Application Support Request"
          >
            Contact Support
          </v-btn>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component } from 'vue-property-decorator'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import { Role } from '@/util/constants'
import Vue from 'vue'
import { mapState } from 'pinia'
import { useUserStore } from '@/stores/user'

@Component({
  computed: {
    ...mapState(useUserStore, ['currentUser'])
  }
})
export default class UnauthorizedView extends Vue {
  readonly currentUser!: KCUserProfile
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
</style>
