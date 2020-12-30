<template>
  <v-container class="terms-of-use-container view-container">

    <!-- Loading status -->
    <v-fade-transition>
      <div class="loading-container" v-if="isLoading">
        <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
      </div>
    </v-fade-transition>

    <div v-if="!isLoading">
      <v-alert type="warning" icon="mdi-alert-circle-outline" class="pa-5 mb-8"
        v-if="showTosBanner"
      >{{$t('tos_updated')}}
      </v-alert>
      <h1 class="mb-10">BC Registry Terms and Conditions</h1>
      <v-card flat>
        <v-card-text class="pa-8">

          <TermsOfUse
            @tos-version-updated="showUpdateBanner"
          ></TermsOfUse>

        </v-card-text>
        <v-card-actions class="terms-of-use-btns justify-center pt-0 pb-8">
          <v-btn
            large
            color="primary"
            class="font-weight-bold"
            @click="clickAccepted"
            data-test="accept-button"
          >
            Accept Terms
          </v-btn>
          <v-btn
            large
            color="default"
            @click="clickDecline"
            data-test="decline-button"
          >
            Decline
          </v-btn>
        </v-card-actions>
      </v-card>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { LoginSource, Pages } from '@/util/constants'
import { mapActions, mapState } from 'vuex'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import TermsOfUse from '@/components/auth/common/TermsOfUse.vue'
import { TermsOfUseDocument } from '@/models/TermsOfUseDocument'
import { User } from '@/models/user'
import UserModule from '@/store/modules/user'
import Vue from 'vue'

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

  private onScroll (e) {
    this.atBottom = (e.target.scrollHeight - e.target.scrollTop) <= (e.target.offsetHeight + 25)
  }

  mounted () {
    this.$store.commit('updateHeader')
  }

  showUpdateBanner () {
    this.showTosBanner = true
  }

  private async clickAccepted () {
    this.isLoading = true
    try {
      await this.updateCurrentUserTerms({
        termsOfUseAcceptedVersion: this.termsOfUse.versionId,
        isTermsOfUseAccepted: true
      })
      const userTerms = await this.saveUserTerms()
      if (userTerms?.userTerms?.isTermsOfUseAccepted) {
        await this.syncUser()
        // if there is a token in the url , that means user is in the invitation flow
        // so after TOS , dont create accont , rather let him create profile if he is not bcros user
        const isBcrosUser = this.currentUser?.loginSource === LoginSource.BCROS
        if (!isBcrosUser && this.token) {
          this.$router.push(`/${Pages.USER_PROFILE}/${this.token}`)
          return
        }
        this.redirectTo(this.getNextPageUrl())
      }
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log(error)
      this.isLoading = false
    }
  }

  private clickDecline () {
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

  section {
    margin-top: 2rem;
  }

  h2 {
    margin-bottom: 2rem;
  }

  ul {
    list-style-type: none;
    padding-left: 50px !important;
  }

  li {
    position: relative;

    span {
      display: inline-block;
      width: 50px;
      margin-left: -50px;
      font-size: 0.9375rem;
    }
  }

  li + li {
    margin-top: 1rem;
  }
</style>
