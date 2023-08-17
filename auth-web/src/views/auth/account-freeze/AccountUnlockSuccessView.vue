<template>
  <v-container class="view-container">
    <v-row justify="center">
      <v-col
        cols="12"
        sm="6"
        class="text-center"
      >
        <template v-if="isFailed">
          <v-icon
            size="32"
            color="error"
            class="mb-6"
          >
            mdi-alert-circle-outline
          </v-icon>
          <h1>Some error occured</h1>
          <p class="mt-8 mb-10">
            Unable to get the status of the organization, Please try again
          </p>
          <div class="btns">
            <v-btn
              large
              color="primary"
              class="action-btn font-weight-bold"
              @click="goTo('account-unlock')"
            >
              Try Again
            </v-btn>
          </div>
        </template>
        <template v-else>
          <v-icon
            size="48"
            color="primary"
            class="mb-6"
          >
            mdi-check
          </v-icon>
          <h1>Your account was successfully unlocked</h1>
          <div class="mt-8 mb-10">
            <div>Your account has successfully been unlocked,</div>
            <div>Thank you for unlocking your account.</div>
          </div>
          <div class="btns">
            <v-btn
              large
              color="primary"
              class="action-btn font-weight-bold"
              @click="goTo('account-info')"
            >
              Ok
            </v-btn>
          </div>
        </template>
      </v-col>
    </v-row>
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
  </v-container>
</template>

<script lang="ts">

import { AccountStatus, Pages } from '@/util/constants'
import { Component, Mixins } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import AccountMixin from '@/components/auth/mixins/AccountMixin.vue'
import { Organization } from '@/models/Organization'

@Component({
  computed: {
    ...mapState('org', ['currentOrganization'])
  },
  methods: {
    ...mapActions('org', ['syncOrganization'])
  }
})
export default class AccountUnlockSuccessView extends Mixins(AccountMixin) {
  protected readonly currentOrganization!: Organization
  protected readonly syncOrganization!: (orgId: number) => Promise<Organization>
  isLoading: boolean = false
  isFailed: boolean = false
  errorMsg: string = ''
  readonly TIMEOUT_DURATION = 10000

  goTo (page) {
    switch (page) {
      case 'account-info': this.$router.push(`/${Pages.MAIN}/${this.currentOrganization.id}/settings/account-info`)
        break
      case 'transactions': this.$router.push(`/${Pages.MAIN}/${this.currentOrganization.id}/settings/transactions`)
        break
      case 'account-unlock': this.$router.push(`/${Pages.ACCOUNT_FREEZE_UNLOCK}`)
        break
    }
  }

  private async mounted () {
    this.isLoading = true
    this.isFailed = false
    let count = 0
    let timerId = setInterval(async () => {
      // eslint-disable-next-line no-console
      console.log(`[OrgRefreshTimer] Org refresh ${++count}`)
      if (this.currentOrganization?.statusCode !== AccountStatus.ACTIVE) {
        await this.syncOrganization(this.currentOrganization?.id)
      } else {
        // eslint-disable-next-line no-console
        console.log('[OrgRefreshTimer] Org refresh stopped (ACTIVE)')
        clearInterval(timerId)
        this.isLoading = false
      }
    }, 3000)
    setTimeout(() => {
      // eslint-disable-next-line no-console
      console.log('[OrgRefreshTimer] Org refresh stopped')
      clearInterval(timerId)
      this.isLoading = false
      this.isFailed = (this.currentOrganization?.statusCode !== AccountStatus.ACTIVE)
    }, this.TIMEOUT_DURATION)
  }
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";

  .action-btn {
    width: 8rem;
  }
</style>
