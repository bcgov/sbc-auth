// You can declare a mixin as the same style as components.
<script lang="ts">
import { AccessType, Account, SessionStorageKeys } from '@/util/constants'
import { AccountSettings } from '@/models/account-settings'
import Component from 'vue-class-component'
import ConfigHelper from '@/util/config-helper'
import { Organization } from '@/models/Organization'
import Vue from 'vue'
import { mapState } from 'vuex'
@Component({
  name: 'AccountMixin',
  computed: {
    ...mapState('user', [
      'currentUser'
    ]),
    ...mapState('org', [
      'currentOrganization',
      'currentMembership'
    ])
  }
})
// TODO in the mounted ; do load all the properties if its not loaded already
export default class AccountMixin extends Vue {
  protected readonly currentOrganization!: Organization

  protected getAccountFromSession (): AccountSettings {
    return JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.CurrentAccount || '{}'))
  }
  protected get isPremiumAccount (): boolean {
    return this.currentOrganization?.orgType === Account.PREMIUM
  }
  protected get isRegularAccount (): boolean {
    return this.currentOrganization?.accessType === AccessType.REGULAR
  }

  protected get anonAccount (): boolean {
    return this.currentOrganization?.accessType === AccessType.ANONYMOUS
  }

  protected get isGovmAccount (): boolean {
    return this.currentOrganization?.accessType === AccessType.GOVM
  }

  protected get isGovnAccount (): boolean {
    return this.currentOrganization?.accessType === AccessType.GOVN
  }

  // Note: this hasn't been migrated on the backend yet.
  protected get isStaffAccount (): boolean {
    return this.currentOrganization?.orgType === Account.STAFF
  }

  protected get isSbcStaffAccount (): boolean {
    return this.currentOrganization?.orgType === Account.SBC_STAFF
  }
}
</script>
