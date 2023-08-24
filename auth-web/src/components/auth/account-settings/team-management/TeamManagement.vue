<template>
  <v-container class="team-mgmt-container">
    <UserManagement
      v-if="!isAnonymousAccount()"
    />
    <AnonymousUserManagement
      v-if="isAnonymousAccount()"
    />
  </v-container>
</template>

<script lang="ts">
import { AccessType, Role } from '@/util/constants'
import { Component, Mixins, Prop } from 'vue-property-decorator'
import AnonymousUserManagement from '@/components/auth/account-settings/team-management/AnonymousUserManagement.vue'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import UserManagement from '@/components/auth/account-settings/team-management/UserManagement.vue'
import { mapState } from 'pinia'
import { useOrgStore } from '@/stores/org'

@Component({
  components: {
    UserManagement,
    AnonymousUserManagement
  },
  computed: {
    ...mapState(useOrgStore, [
      'currentMembership',
      'currentOrganization'
    ])
  },
  methods: {

  }
})
export default class TeamManagement extends Mixins(NextPageMixin) {
  @Prop({ default: '' }) private orgId: string

  private async mounted () {
    // redirect to dir search/team management according to dir search user role change
    if (this.isAnonymousAccount() && !this.currentUser.roles.includes(Role.Staff)) {
      this.redirectTo(this.getNextPageUrl())
    }
  }
  private isAnonymousAccount (): boolean {
    return this.currentOrganization &&
            this.currentOrganization.accessType === AccessType.ANONYMOUS
  }
}
</script>

<style lang="scss" scoped>
  .team-mgmt-container {
    overflow: hidden;
  }
</style>
