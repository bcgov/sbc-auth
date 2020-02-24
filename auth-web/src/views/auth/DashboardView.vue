<template>
  <div class="dashboard-view">
    <article>
      <router-view></router-view>
    </article>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { Member, MembershipStatus, Organization } from '@/models/Organization'
import { mapActions, mapGetters, mapState } from 'vuex'
import EntityManagement from '@/components/auth/EntityManagement.vue'
import { User } from '@/models/user'
import UserManagement from '@/components/auth/UserManagement.vue'
import { VueConstructor } from 'vue'

  @Component({
    name: 'Dashboard',
    components: {
      EntityManagement,
      UserManagement
    },
    computed: {
      ...mapState('user', ['userProfile']),
      ...mapState('org', ['currentOrganization', 'currentMembership'])
    },
    methods: {
      ...mapActions('user', ['getUserProfile']),
      ...mapActions('org', ['syncMembership'])
    }
  })
export default class DashboardView extends Vue {
  private selectedComponent = null
  private readonly userProfile!: User
  private readonly currentOrganization!: Organization
  private readonly currentMembership!: Member
  private readonly getUserProfile!: (identifier: string) => User
  private readonly syncMembership!: (orgId: number) => Member

  private menu = [
    {
      title: 'Manage Businesses',
      icon: 'business',
      testTag: 'manage-business-nav',
      path: 'business'
    }
  ]

  async mounted () {
    // Check for existing state, and if not tell store to update
    if (!this.userProfile) {
      this.getUserProfile('@me')
    }

    // Check the current user's team status
    // TODO: For now this means checking their single team, later it will mean checking the active team.
    await this.redirectBasedOnTeamStatus()
  }

  setSelectedComponent (selectedComponent: VueConstructor) {
    this.selectedComponent = selectedComponent
  }

  private async redirectBasedOnTeamStatus (): Promise<void> {
    // Sync membership first since it may have changed since they signed in (#2483)
    await this.syncMembership(this.currentOrganization.id)

    // If user is pending approval by an admin, redirect to pending approval page
    if (this.currentMembership && this.currentMembership.membershipStatus === MembershipStatus.Pending) {
      this.$router.push(`/pendingapproval/${this.currentOrganization.name}`)
    }

    // If user is not an active member of a team at all, redirect to create team page
    if (!this.currentMembership) {
      this.$router.push('/createaccount')
    }
  }
}
</script>
