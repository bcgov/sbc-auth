<template>
  <div>
    <template v-if="!invalidInvitationToken && !tokenError && !otherError">
      <div v-if="loginSource == loginSourceenum.BCROS">
        <create-user-profile-landing
          :token="token"
          :orgName="orgName"
        ></create-user-profile-landing>
      </div>
      <div v-if="loginSource == loginSourceenum.BCEID">
        <interim-landing
          :summary="$t('acceptInviteLandingTitle')"
          :description="$t('acceptInviteLandingMessageBCEID')"
          icon="mdi-login-variant"
          showHomePageBtn="false"
          v-if="affidavitNeeded"
        >
          <template v-slot:actions>
            <v-btn

              large
              link
              color="primary"
              @click="bceidAcceptinviteWithAffidavit()"
              >Accept</v-btn
            >

          </template>
        </interim-landing>

        <bceid-invite-landing
          :token="token"
          :orgName="orgName"
          v-else
        ></bceid-invite-landing>
      </div>
      <div v-if="loginSource == loginSourceenum.BCSC">
        <interim-landing
          :summary="$t('acceptInviteLandingTitle')"
          :description="$t('acceptInviteLandingMessage')"
          icon="mdi-login-variant"
          showHomePageBtn="false"
        >
          <template v-slot:actions>
            <v-btn
              v-if="!isUserSignedIn()"
              large
              link
              color="primary"
              @click="redirectToSignin()"
              >{{ $t('loginBtnLabel') }}</v-btn
            >
            <v-btn
              v-if="isUserSignedIn()"
              large
              link
              color="primary"
              @click="redirectToConfirm()"
              >{{ $t('acceptButtonLabel') }}</v-btn
            >
          </template>
        </interim-landing>
      </div>
    </template>
    <div v-if="invalidInvitationToken">
      <interim-landing
        :summary="$t('expiredInvitationTitle')"
        :description="$t('expiredInvitationMessage')"
        icon="mdi-alert-circle-outline"
        iconColor="error"
      >
      </interim-landing>
    </div>
    <div v-if="tokenError || otherError">
      <interim-landing
        :summary="$t('errorOccurredTitle')"
        :description="$t('invitationProcessingErrorMsg')"
        icon="mdi-alert-circle-outline"
        iconColor="error"
      >
      </interim-landing>
    </div>
  </div>
</template>

<script lang="ts">

import { Component, Prop, Vue } from 'vue-property-decorator'
import { LoginSource, SessionStorageKeys } from '@/util/constants'
import { mapActions, mapState } from 'vuex'
import BceidInviteLanding from '@/components/auth/BceidInviteLanding.vue'
import ConfigHelper from '@/util/config-helper'
import CreateUserProfileLanding from '@/components/auth/CreateUserProfileLanding.vue'
import { EmptyResponse } from '@/models/global'
import InterimLanding from '@/components/auth/common/InterimLanding.vue'
import OrgModule from '@/store/modules/org'
import { getModule } from 'vuex-module-decorators'

@Component({
  computed: {
    ...mapState('org', ['invalidInvitationToken', 'tokenError'])
  },
  methods: {
    ...mapActions('org', ['validateInvitationToken'])
  },
  components: {
    BceidInviteLanding,
    InterimLanding,
    CreateUserProfileLanding
  }
})
export default class AcceptInviteLandingView extends Vue {
  private orgStore = getModule(OrgModule, this.$store)
  private readonly validateInvitationToken!: (token: string) => EmptyResponse
  private readonly invalidInvitationToken!: boolean
  private readonly tokenError!: boolean

  @Prop() token: string
  @Prop({ default: '' }) orgName: string
  @Prop({ default: LoginSource.BCSC }) loginSource: string

  private otherError: boolean = false
  private isCreateUserProfile: boolean = false
  private affidavitNeeded: boolean = false

  public async mounted () {
    // if user need to go through affidavit upload. invitation URL will have ?affidavit=truetype
    // take that value and set in session storage inchild component
    this.affidavitNeeded = this.$route.query.affidavit
      ? true
      : this.affidavitNeeded
    // if no value for loginSource , defaulted to bcsc
    // if loginSource =bcros , take them to create user profile
    // if loginSource bcsc , stay in the page , show inivtation accept screen
    // if loginSource = bceid ,take to bceid login page
    this.isCreateUserProfile = this.loginSource === LoginSource.BCROS
    await this.validateToken()
    // make sure token is valid
    const allCheckPassed =
      !this.invalidInvitationToken && !this.tokenError && !this.otherError
    // if login source is IDIR. it will be GOVM account and need to re-direct to IDIR login page
    if (
      allCheckPassed &&
      this.loginSource.toLowerCase() === LoginSource.IDIR.toLowerCase()
    ) {
      this.redirectToSignin('idir')
    }
  }

  get loginSourceenum () {
    return LoginSource
  }

  private isUserSignedIn (): boolean {
    return !!ConfigHelper.getFromSession('KEYCLOAK_TOKEN')
  }

  private redirectToSignin (loginSourceUrl: string = 'bcsc') {
    let redirectUrl = `${ConfigHelper.getSelfURL()}/confirmtoken/${
      this.token
    }/${loginSourceUrl}`
    this.$router.push(
      `/signin/${loginSourceUrl}/${encodeURIComponent(redirectUrl)}`
    )
  }

  private redirectToConfirm () {
    this.$router.push('/confirmtoken/' + this.token)
  }

  private bceidAcceptinviteWithAffidavit () {
    if (!this.isUserSignedIn()) {
      this.setStorage()
    }

    this.$router.push('/nonbcsc-info')
  }

  private setStorage () {
    ConfigHelper.addToSession(SessionStorageKeys.InvitationToken, this.token)
    ConfigHelper.addToSession(SessionStorageKeys.AffidavitNeeded, this.affidavitNeeded)
  }

  async validateToken () {
    try {
      await this.validateInvitationToken(this.token)
    } catch (exception) {
      this.otherError = true
    }
  }
}
</script>
