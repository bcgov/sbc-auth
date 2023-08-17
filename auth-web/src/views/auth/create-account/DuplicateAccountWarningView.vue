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
        <v-card
          v-for="(org, index) in orgsOfUser"
          :key="index"
          flat
          class="my-4 d-flex justify-space-between align-center pa-8"
        >
          <div class="d-flex align-center">
            <div>
              <v-avatar
                tile
                left
                color="#4d7094"
                size="32"
                class="user-avatar"
              >
                <strong>{{ org.name && org.name.slice(0,1) && org.name.slice(0,1).toUpperCase() }}</strong>
              </v-avatar>
            </div>
            <div class="text-left ml-2">
              <h4 class="font-weight-bold ">
                {{ org.name }}
              </h4>
              <p class="mb-0">
                {{ org.addressLine }}
              </p>
            </div>
          </div>
          <div class="text-right">
            <v-btn
              large
              color="primary"
              title="Access Account"
              data-test="goto-access-account-button"
              @click="navigateToRedirectUrl(org.id)"
            >
              Access Account
            </v-btn>
          </div>
        </v-card>
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
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'
import { OrgWithAddress, Organization } from '@/models/Organization'
import { Address } from '@/models/address'
import { Pages } from '@/util/constants'
import { UserSettings } from '@/models/user'
import { namespace } from 'vuex-class'

const OrgModule = namespace('org')
const UserModule = namespace('user')

@Component({})
export default class DuplicateAccountWarningView extends Vue {
    @UserModule.State('currentUserAccountSettings') private currentUserAccountSettings!: UserSettings[]
    @UserModule.Action('getUserAccountSettings') private getUserAccountSettings!: () => Promise<any>

    @OrgModule.Action('getOrgAdminContact') private getOrgAdminContact!: (orgId: number) => Promise<Address>
    @OrgModule.State('currentOrganization') private currentOrganization!: Organization
    @OrgModule.Action('addOrgSettings') private addOrgSettings!: (currentOrganization: Organization) => Promise<UserSettings>
    @OrgModule.Action('syncOrganization') private syncOrganization!: (orgId: number) => Promise<Organization>

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
                addressLine: orgAdminContact ? `${orgAdminContact.street} ${orgAdminContact.city} ` +
                `${orgAdminContact.region} ${orgAdminContact.postalCode} ${orgAdminContact.country}` : null
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
      this.$store.commit('updateHeader')
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
  @import '$assets/scss/theme.scss';

    .v-list-item__title {
      line-height: 1.5rem;
    }

    .v-list-item__subtitle {
      line-height: 1rem;
    }
    .user-avatar {
      margin-right: 0.75rem;
      color: var(--v-accent-lighten5);
      border-radius: 0.15rem;
      font-size: 1.1875rem;
      font-weight: 700;
    }
</style>
