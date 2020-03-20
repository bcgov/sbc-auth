<template>
  <v-container>
    <UserManagement
      v-if="!isAnonymousAccount()"
      :can-invite="canInvite()"></UserManagement>
    <AnonymousUserManagement
        v-if="isAnonymousAccount()"
        :can-invite="canInvite()"></AnonymousUserManagement>

  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { Member, MembershipStatus, MembershipType, Organization } from '@/models/Organization'
import { mapActions, mapState } from 'vuex'

import AnonymousUserManagement from '@/components/auth/AnonymousUserManagement.vue'
import { Event } from '@/models/event'
import MemberDataTable from '@/components/auth/MemberDataTable.vue'
import ModalDialog from '@/components/auth/ModalDialog.vue'
import OrgModule from '@/store/modules/org'
import { SessionStorageKeys } from '@/util/constants'
import UserManagement from '@/components/auth/UserManagement.vue'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    UserManagement,
    AnonymousUserManagement
  },
  computed: {
    ...mapState('org', [
      'currentMembership',
      'currentOrganization'
    ])
  },
  methods: {

  }
})
export default class TeamManagement extends Vue {
  @Prop({ default: '' }) private orgId: string;

  private readonly currentMembership!: Member
  private readonly currentOrganization!: Organization

  private async mounted () {
  }

  private canInvite (): boolean {
    return this.currentMembership &&
            this.currentMembership.membershipStatus === MembershipStatus.Active &&
            (this.currentMembership.membershipTypeCode === MembershipType.Owner ||
             this.currentMembership.membershipTypeCode === MembershipType.Admin)
  }

  private isAnonymousAccount (): boolean {
    return this.currentOrganization &&
            this.currentOrganization.access_type === 'ANONYMOUS'
  }
}
</script>

<style lang="scss" scoped>

</style>
