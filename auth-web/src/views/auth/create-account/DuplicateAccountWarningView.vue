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
     <template v-if="orgsOfUser.length > 0">
        <v-list dense class="pt-0 pb-0">
          <template v-for="(org, index) in orgsOfUser">
            <v-divider class="mt-1 mb-1" :key="index"></v-divider>
            <v-list-item :key="org.id">
                <v-list-item-content>
                    <v-list-item-title>{{ org.name }}</v-list-item-title>
                    <v-list-item-subtitle>{{ org.addressLine }}</v-list-item-subtitle>
                </v-list-item-content>
            </v-list-item>
          </template>
        </v-list>
      </template>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { User, UserSettings } from '@/models/user'
import { Address } from '@/models/address'
import { OrgWithAddress } from '@/models/Organization'
import { namespace } from 'vuex-class'

const OrgModule = namespace('org')
const UserModule = namespace('user')

@Component({})
export default class DuplicateAccountWarningView extends Vue {
    @UserModule.Action('getUserSettings') private getUserSettings!: (keycloakGuid: string) => Promise<any>
    @UserModule.State('userProfile') private userProfile!: User
    @UserModule.Action('getUserProfile') private getUserProfile!: (identifier: string) => Promise<User>
    @OrgModule.Action('getOrgAdminContact') private getOrgAdminContact!: (orgId: number) => Promise<Address>
    private orgsOfUser: OrgWithAddress[] = []

    private async mounted () {
      try {
        await this.getUserProfile('@me')
        const userSettings: UserSettings[] = await this.getUserSettings(this.userProfile?.keycloakGuid)
        for (let i = 0; i < userSettings.length && userSettings.length > 0; i++) {
          const orgId = parseInt(userSettings[i].id)
          const orgAdminContact = await this.getOrgAdminContact(orgId)
          const orgOfUser: OrgWithAddress = {
            id: orgId,
            name: userSettings[i].label,
            addressLine: `${orgAdminContact.street} 
            ${orgAdminContact.city} ${orgAdminContact.region} ${orgAdminContact.postalCode} ${orgAdminContact.country}`
          }
          this.orgsOfUser.push(orgOfUser)
        }
      } catch (err) {
        // eslint-disable-next-line no-console
        console.log(`Error while loading duplicate accounts ${err}`)
      }
    }
}
</script>

<style>

</style>
