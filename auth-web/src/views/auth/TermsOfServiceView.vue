<template>
  <v-container class="terms-of-use-container view-container">
    <!-- Loading status -->
    <v-fade-transition>
      <div
        v-if="isLoading"
        class="loading-container"
      >
        <v-progress-circular
          size="50"
          width="5"
          color="primary"
          :indeterminate="isLoading"
        />
      </div>
    </v-fade-transition>

    <div v-if="!isLoading">
      <v-alert
        v-if="showTosBanner"
        type="warning"
        icon="mdi-alert-circle-outline"
        class="pa-5 mb-8"
      >
        {{ $t(isGovmUser ? 'govm_tos_updated' : 'tos_updated') }}
      </v-alert>
      <h1 class="mb-10">
        {{ $t(isGovmUser ? 'govm_tos_title' : 'tos_title') }}
      </h1>

      <v-card flat>
        <v-card-text class="pa-8">
          <TermsOfUse
            @tos-version-updated="showUpdateBanner"
          />
        </v-card-text>
        <v-card-actions class="terms-of-use-btns justify-center pt-0 pb-8">
          <v-btn
            large
            color="primary"
            class="font-weight-bold"
            data-test="accept-button"
            @click="clickAccepted"
          >
            Accept Terms
          </v-btn>
          <v-btn
            large
            color="default"
            data-test="decline-button"
            @click="clickDecline"
          >
            Decline
          </v-btn>
        </v-card-actions>
      </v-card>
    </div>
  </v-container>
</template>

<script lang="ts">
import { ALLOWED_URIS_FOR_PENDING_ORGS, LoginSource, Pages } from '@/util/constants'
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import TermsOfUse from '@/components/auth/common/TermsOfUse.vue'
import { TermsOfUseDocument } from '@/models/TermsOfUseDocument'
import { User } from '@/models/user'
/* eslint-disable-next-line @typescript-eslint/no-unused-vars */
import UserModule from '@/store/modules/user'

@Component({
  components: {
    TermsOfUse
  },
  computed: {
    ...mapState('user', ['termsOfUse'])
  },
  methods: {
    ...mapActions('user',
      [
        'saveUserTerms',
        'updateCurrentUserTerms'
      ]
    )
  }
})
export default class TermsOfServiceView extends Mixins(NextPageMixin) {
  private readonly saveUserTerms!: () => Promise<User>
  private readonly updateCurrentUserTerms!: (UserTerms) => void
  private readonly termsOfUse!: TermsOfUseDocument
  private isLoading: boolean = false
  private atBottom = false
  @Prop() token: string

  protected readonly currentUser!: KCUserProfile
  private showTosBanner = false
  private isGovmUser: boolean = false

  private onScroll (e) {
    this.atBottom = (e.target.scrollHeight - e.target.scrollTop) <= (e.target.offsetHeight + 25)
  }

  mounted () {
    this.$store.commit('updateHeader')
    this.isGovmUser = this.isGovmUserLoggedin()
  }

  isGovmUserLoggedin () {
    return this.currentUser?.loginSource.toUpperCase() === LoginSource.IDIR.toUpperCase()
  }

  showUpdateBanner () {
    this.showTosBanner = true
  }

  isGovmAndHasToken () : boolean {
    return this.isGovmUser && !!this.token
  }

  isNotBCROSUserAndHasToken (): boolean {
    return this.currentUser?.loginSource !== LoginSource.BCROS && !!this.token
  }

  async clickAccepted () {
    this.isLoading = true
    const affidavitNeeded = !!this.$route.query.affidavit

    try {
      await this.updateCurrentUserTerms({
        termsOfUseAcceptedVersion: this.termsOfUse.versionId,
        isTermsOfUseAccepted: true
      })
      const userTerms = await this.saveUserTerms()
      if (!userTerms?.userTerms?.isTermsOfUseAccepted) {
        return
      }
      await this.syncUser()

      // if this IDIR GOVM , user take him to accept invite itself.
      // IDIR user doesnt have user profile.so next page mixin will yield wrong navigation if used here.
      if (this.isGovmAndHasToken()) {
        this.$router.push(`/confirmtoken/${this.token}/${LoginSource.IDIR}`)
        return
      }
      // if there is a token in the url , that means user is in the invitation flow
      // so after TOS , dont create accont , rather let him create profile if he is not bcros user
      if (this.isNotBCROSUserAndHasToken()) {
      // if user is in affidavit flow we need redirect to affidavit upload instead of user profile
        if (affidavitNeeded) {
          await this.$router.push(`/${Pages.AFFIDAVIT_COMPLETE}/${this.token}`)
          return
        }
        this.$router.push(`/${Pages.USER_PROFILE}/${this.token}`)
        return
      }
      // special logic for handling redirection to create account page
      // if we dont redirect back to original page , pending org update flow wont work
      const redirectUri = this.$route?.query?.redirectUri as string
      if (redirectUri) {
        const substringCheck = (element:string) => redirectUri.indexOf(element) > -1
        let isAllowedUrl = ALLOWED_URIS_FOR_PENDING_ORGS.findIndex(substringCheck) > -1
        if (isAllowedUrl) {
          await this.$router.push(redirectUri)
          return
        }
      }
      this.redirectTo(this.getNextPageUrl())
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log(error)
      this.isLoading = false
    }
  }

  clickDecline () {
    this.$router.push(`/${Pages.USER_PROFILE_TERMS_DECLINE}`)
  }
}
</script>

<style lang="scss" scoped>
  .terms-of-use-container {
    max-width: 65rem;
  }

  .terms-of-use-btns {
    .v-btn {
      width: 8rem;
    }
  }
</style>
