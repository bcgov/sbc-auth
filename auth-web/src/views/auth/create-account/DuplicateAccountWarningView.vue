<template>
  <v-container class="view-container">
    <v-row justify="center">
      <v-col
        cols="12"
        sm="8"
        md="6"
        class="text-center pb-0"
      >
        <v-icon
          large
          color="error"
          class="font-weight-bold"
        >
          mdi-alert-circle-outline
        </v-icon>
        <h1 class="view-header__title text-center mt-3 px-12">
          Looks like you already have an account
        </h1>
        <p
          class="text-center my-3 pl-3 pr-3 mt-8"
          v-html="$t('duplicateAccountWarningViewMessage')"
        />
        <p class="mt-6 pb-0 justify-center d-flex font-weight-bold ">
          Use one of the existing accounts:
        </p>
      </v-col>
    </v-row>
    <v-row
      v-if="orgsOfUser.length > 0 && !isLoading"
      justify="center"
    >
      <v-col
        cols="12"
        sm="9"
        md="7"
        class="text-center"
      >
        <account-select-list
          :accounts="orgsOfUser"
          action-label="Access Account"
          @select="navigateToRedirectUrl"
        />
      </v-col>
    </v-row>
    <v-row justify="center">
      <v-col
        cols="12"
        sm="8"
        md="6"
        class="text-center"
      >
        <v-btn
          large
          outlined
          color="primary"
          data-test="goto-create-account-button"
          @click="createAccount()"
        >
          Create Another Account
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Action, State } from 'pinia-class'
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'
import { OrgWithAddress, Organization } from '@/models/Organization'
import AccountSelectList from '@/components/auth/common/AccountSelectList.vue'
import { Address } from '@/models/address'
import CommonUtils from '@/util/common-util'
import { Pages } from '@/util/constants'
import { UserSettings } from '@/models/user'
import { useAppStore } from '@/stores'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

@Component({
  components: {
    AccountSelectList
  }
})
export default class DuplicateAccountWarningView extends Vue {
    @State(useUserStore) private currentUserAccountSettings!: UserSettings[]
    @Action(useUserStore) private getUserAccountSettings!: () => Promise<any>

    @Action(useOrgStore) private getOrgAdminContact!: (orgId: number) => Promise<Address>
    @State(useOrgStore) private currentOrganization!: Organization
    @Action(useOrgStore) private addOrgSettings!: (currentOrganization: Organization) => Promise<UserSettings>
    @Action(useOrgStore) private syncOrganization!: (orgId: number) => Promise<Organization>

    private orgsOfUser: OrgWithAddress[] = []
    private isLoading: boolean = false
    @Prop({ default: '' }) redirectToUrl !: string

    private async mounted () {
      if (!this.currentUserAccountSettings?.length) {
        await this.getUserAccountSettings()
      }
    }
    @Watch('currentUserAccountSettings', { immediate: true })
    private async onCurrentUserAccountSettings (): Promise<void> {
      try {
        if (this.currentUserAccountSettings?.length) {
          this.isLoading = true
          this.orgsOfUser = await Promise.all(
            this.currentUserAccountSettings.map(async (accountsetting: UserSettings) => {
              const orgId = parseInt(accountsetting.id)
              const orgAdminContact = await this.getOrgAdminContact(orgId)
              const orgOfUser: OrgWithAddress = {
                id: orgId,
                name: accountsetting.label,
                addressLine: CommonUtils.formatAddressLine(orgAdminContact)
              }
              return orgOfUser
            }
            ))
        }
      } catch (err) {
        // eslint-disable-next-line no-console
        console.log(`Error while loading duplicate accounts ${err}`)
      } finally {
        this.isLoading = false
      }
    }

    private async navigateToRedirectUrl (accountId: number): Promise<void> {
      await this.syncOrganization(accountId)
      await this.addOrgSettings(this.currentOrganization)
      useAppStore().updateHeader()
      if (this.redirectToUrl) {
        window.location.assign(this.redirectToUrl.toString())
      } else {
        this.$router.push(`/${Pages.HOME}`)
      }
    }

    private createAccount () {
      this.$router.push(`/${Pages.CREATE_ACCOUNT}?skipConfirmation=true`)
    }
}
</script>

<style lang="scss" scoped>
    .v-list-item__title {
      line-height: 1.5rem;
    }

    .v-list-item__subtitle {
      line-height: 1rem;
    }
</style>
