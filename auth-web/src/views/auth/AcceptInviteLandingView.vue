<template>
  <div>
    <template v-if="!invalidInvitationToken && !tokenError && !otherError">
      <div v-if="isCreateUserProfile">
        <create-user-profile-landing
          :token="token"
          :orgName="orgName"
        ></create-user-profile-landing>
      </div>
      <div v-if="!isCreateUserProfile">
        <interim-landing :summary="$t('acceptInviteLandingTitle')" :description="$t('acceptInviteLandingMessage')" icon="mdi-login-variant" showHomePageBtn="false">
          <template v-slot:actions>
            <v-btn v-if="!isUserSignedIn()" large link color="primary" @click="redirectToSignin()">{{ $t('loginBtnLabel') }}</v-btn>
            <v-btn v-if="isUserSignedIn()" large link color="primary" @click="redirectToConfirm()">{{ $t('acceptButtonLabel') }}</v-btn>
          </template>
        </interim-landing>
      </div>
    </template>
    <div v-if="invalidInvitationToken">
      <interim-landing :summary="$t('expiredInvitationTitle')" :description="$t('expiredInvitationMessage')" icon="mdi-alert-circle-outline" iconColor="error">
      </interim-landing>
    </div>
    <div v-if="tokenError || otherError">
      <interim-landing :summary="$t('errorOccurredTitle')" :description="$t('invitationProcessingErrorMsg')" icon="mdi-alert-circle-outline" iconColor="error">
      </interim-landing>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import ConfigHelper from '@/util/config-helper'
import CreateUserProfileLanding from '@/components/auth/CreateUserProfileLanding.vue'
import { EmptyResponse } from '@/models/global'
import InterimLanding from '@/components/auth/InterimLanding.vue'
import OrgModule from '@/store/modules/org'
import { Pages } from '@/util/constants'
import { getModule } from 'vuex-module-decorators'

@Component({
  computed: {
    ...mapState('org', ['invalidInvitationToken', 'tokenError'])
  },
  methods: {
    ...mapActions('org', ['validateInvitationToken'])
  },
  components: {
    InterimLanding,
    CreateUserProfileLanding
  }
})
export default class AcceptInviteLandingView extends Vue {
  private orgStore = getModule(OrgModule, this.$store);
  private readonly validateInvitationToken!: (token: string) => EmptyResponse

  @Prop() token: string
  @Prop({ default: '' }) orgName: string

  private otherError: boolean = false
  private isCreateUserProfile: boolean = false

  private mounted () {
    this.isCreateUserProfile = (this.$route?.name === Pages.CREATE_USER_PROFILE)
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
      this.otherError = true
    }
  }
}
</script>
