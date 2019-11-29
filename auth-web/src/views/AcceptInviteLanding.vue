<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" lg="8" class="text-center">
        <div v-if="!tokenExpiry && !tokenError">
          <v-icon size="48" color="primary" class="mb-6">mdi-login-variant</v-icon>
          <h1 class="mb-7">{{ $t('acceptInviteLandingTitle') }}</h1>
          <p class="mb-9">{{ $t('acceptInviteLandingMessage') }}</p>
          <v-btn v-if="!isUserSignedIn()" large link color="primary" @click="redirectToSignin()">{{ $t('loginBtnLabel') }}</v-btn>
          <v-btn v-if="isUserSignedIn()" large link color="primary" @click="redirectToConfirm()">{{ $t('acceptButtonLabel') }}</v-btn>
        </div>
        <div v-if="tokenExpiry">
          <v-icon size="48" color="error" class="mb-6">mdi-alert-circle-outline</v-icon>
          <h1 class="mb-7">{{ $t('expiredInvitationTitle')}}</h1>
          <p class="mb-9">{{ $t('expiredInvitationMessage')}}</p>
          <v-btn large link color="primary" href="../">{{ $t('homeBtnLabel')}}</v-btn>
        </div>
        <div v-if="tokenError">
          <v-icon size="48" color="error" class="mb-6">mdi-alert-circle-outline</v-icon>
          <h1 class="mb-7">{{ $t('errorOccurredTitle')}}</h1>
          <p class="mb-9">{{ $t('invitationProcessingErrorMsg')}}</p>
          <v-btn large link color="primary" href="../">{{ $t('homeBtnLabel')}}</v-btn>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
import { EmptyResponse } from '@/models/global'
import OrgModule from '@/store/modules/org'
import { getModule } from 'vuex-module-decorators'
import { mapActions } from 'vuex'

@Component({
  methods: {
    ...mapActions('org', ['validateInvitationToken'])
  }
})
export default class AcceptInviteLanding extends Vue {
  private orgStore = getModule(OrgModule, this.$store);
  private readonly validateInvitationToken!: (token: string) => EmptyResponse

  @Prop() token: string

  private tokenExpired: boolean = false
  private tokenError: boolean = false

  private mounted () {
    this.validateToken()
  }

  private isUserSignedIn (): boolean {
    return !!ConfigHelper.getFromSession('KEYCLOAK_TOKEN')
  }

  private redirectToSignin () {
    let redirectUrl = ConfigHelper.getSelfURL() + '/confirmtoken/' + this.token
    this.$router.push('/signin/bcsc/' + encodeURIComponent(redirectUrl))
  }

  private redirectToConfirm () {
    this.$router.push('/confirmtoken/' + this.token)
  }

  async validateToken () {
    try {
      await this.validateInvitationToken(this.token)
    } catch (exception) {
      if (exception.status === 400) {
        this.tokenExpired = true
      } else {
        this.tokenError = true
      }
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

  .v-icon {
    font-size: 4rem;
  }
</style>
