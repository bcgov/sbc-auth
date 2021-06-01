<template>
  <v-container>
    <header class="view-header mb-3 d-flex flex-column">
        <v-icon large color="error" class="font-weight-bold">mdi-alert-circle-outline</v-icon>
        <div>
            <h1 class="view-header__title text-center mt-3">Looks like you already have an account</h1>
            <p class="text-center my-3 pl-10 pr-10" v-html="$t('duplicateAccountWarningViewMessage')"/>
        </div>
    </header>
    <div class="mb-3 justify-center d-flex">
      <strong class="font-weight-bold text-center">Use one of the existing accounts:</strong>
    </div>
    <template class="d-flex justify-center mb-6 pb-6">
    <v-card flat v-if="orgsOfUser.length > 0 && !isLoading" class="p-1">
      <v-card-text>
       <v-list dense>
          <template v-for="(org, index) in orgsOfUser">
            <v-divider class="mt-1 mb-1" :key="index" v-if="index>1"></v-divider>
            <v-list-item :key="org.id" class="d-flex flex-row justify-center">
                <v-avatar
                tile
                left
                color="#4d7094"
                size="32"
                class="user-avatar">
                {{ org.name.slice(0,1) }}
                </v-avatar>
                <v-list-item-content>
                    <v-list-item-title><h2 class="font-weight-bold v-list-item__title">{{ org.name }}</h2></v-list-item-title>
                    <v-list-item-subtitle class="mt-3 v-list-item__subtitle"><strong>{{ org.addressLine }}</strong></v-list-item-subtitle>
                </v-list-item-content>
                <v-btn large color="primary" @click="navigateToRedirectUrl(org.id)" title="Go to Business Dashboard" data-test="goto-dashboard-button">Access Account</v-btn>
            </v-list-item>
          </template>
         </v-list>
      </v-card-text>
      <v-card-actions class="justify-center">
        <v-btn large outlined color="primary" @click="createAccount()">
          Create Another Account
        </v-btn>
      </v-card-actions>
    </v-card>
    </template>
  </v-container>
</template>

<script lang="ts">
import { Component, Mixins, Prop, Vue } from 'vue-property-decorator'
import { OrgWithAddress, Organization } from '@/models/Organization'
import { Pages, SessionStorageKeys } from '@/util/constants'
import { User, UserSettings } from '@/models/user'
import { Address } from '@/models/address'
import ConfigHelper from '@/util/config-helper'

import { namespace } from 'vuex-class'

const OrgModule = namespace('org')
const UserModule = namespace('user')

@Component({})
export default class DuplicateAccountWarningView extends Vue {
    @UserModule.State('currentUserAccountSettings') private currentUserAccountSettings!: UserSettings[]
    @OrgModule.Action('getOrgAdminContact') private getOrgAdminContact!: (orgId: number) => Promise<Address>
    @OrgModule.State('currentOrganization') private currentOrganization!: Organization
    @OrgModule.Action('addOrgSettings') private addOrgSettings!: (currentOrganization: Organization) => Promise<UserSettings>
    private orgsOfUser: OrgWithAddress[] = []
    private isLoading: boolean = false
    @Prop({ default: '' }) redirectToUrl !: string

    private async mounted () {
      try {
        this.isLoading = true
        for (let i = 0; i < this.currentUserAccountSettings.length && this.currentUserAccountSettings.length > 0; i++) {
          const orgId = parseInt(this.currentUserAccountSettings[i].id)
          const orgAdminContact = await this.getOrgAdminContact(orgId)
          const orgOfUser: OrgWithAddress = {
            id: orgId,
            name: this.currentUserAccountSettings[i].label,
            addressLine: `${orgAdminContact.street} ${orgAdminContact.city} ${orgAdminContact.region} ${orgAdminContact.postalCode} ${orgAdminContact.country}`
          }
          this.orgsOfUser.push(orgOfUser)
        }
      } catch (err) {
        // eslint-disable-next-line no-console
        console.log(`Error while loading duplicate accounts ${err}`)
      } finally {
        this.isLoading = false
      }
    }

    private async navigateToRedirectUrl (accountId: number): Promise<void> {
      await this.addOrgSettings(this.currentOrganization)
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
    }
</style>
