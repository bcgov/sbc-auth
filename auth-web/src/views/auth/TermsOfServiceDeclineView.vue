<template>
  <v-container class="view-container">
    <v-row justify="center">
      <v-col
        cols="12"
        lg="6"
        class="text-center"
      >
        <v-icon
          size="48"
          color="error"
          class="mb-6"
        >
          mdi-information-outline
        </v-icon>
        <h1 class="mb-5">
          Not Authorized
        </h1>
        <p class="mb-9">
          {{ errorMessage }}
        </p>
        <div>
          <v-btn
            large
            color="primary"
            @click="navigate('termsofuse')"
          >
            Terms of Use
          </v-btn>
          <v-btn
            large
            color="default"
            class="ml-4"
            @click="navigate('logout')"
          >
            Log out
          </v-btn>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { LoginSource, Pages } from '@/util/constants'
import { Component } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'

import Vue from 'vue'
import { mapState } from 'pinia'
import { useUserStore } from '@/store/user'

@Component({
  computed: {
    ...mapState(useUserStore, ['currentUser'])
  }
})
export default class UnauthorizedView extends Vue {
  currentUser!: KCUserProfile
  errorMessage : string = ''

  mounted () {
    this.errorMessage = this.$t('dirSearchUnauthorizedMsg').toString()
  }

  navigate (page) {
    switch (page) {
      case 'termsofuse': this.$router.push(`/${Pages.USER_PROFILE_TERMS}`)
        break
      case 'logout':
        if (this.currentUser?.loginSource === LoginSource.BCROS) {
          let redirectUrl = `${ConfigHelper.getSelfURL()}/signin/bcros/`
          this.$router.push(`/${Pages.SIGNOUT}/${encodeURIComponent(redirectUrl)}`)
        } else {
          this.$router.push(`/${Pages.SIGNOUT}`)
        }
        break
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";

  .v-btn {
    width: 8rem;
  }

  .v-btn.primary {
    font-weight: 700;
  }
</style>
