<template>
  <div class="dashboard-view">
    <ManagementMenu :menu="menu" />
    <article>
      <component
        :is="selectedComponent"
        @change-to="setSelectedComponent($event)"
      />
    </article>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { Member, MembershipStatus, MembershipType, Organization } from '@/models/Organization'
import { mapActions, mapGetters, mapState } from 'vuex'
import ConfigHelper from '@/util/config-helper'
import EntityManagement from '@/views/management/EntityManagement.vue'
import ManagementMenu from '@/components/auth/ManagementMenu.vue'
import { User } from '@/models/user'
import UserManagement from '@/views/management/UserManagement.vue'
import { VueConstructor } from 'vue'

@Component({
  name: 'Dashboard',
  components: {
    ManagementMenu,
    EntityManagement,
    UserManagement
  },
  computed: {
    ...mapState('user', ['userProfile']),
    ...mapState('org', ['currentOrganization']),
    ...mapGetters('org', ['myOrgMembership'])
  },
  methods: {
    ...mapActions('user', ['getUserProfile']),
    ...mapActions('org', ['syncOrganizations', 'syncCurrentOrganization'])
  }
})
export default class Dashboard extends Vue {
  private selectedComponent = null
  private readonly userProfile!: User
  private readonly currentOrganization!: Organization
  private readonly myOrgMembership!: Member
  private readonly getUserProfile!: (identifier: string) => User
  private readonly syncOrganizations!: () => Organization[]
  private readonly syncCurrentOrganization!: (organization: Organization) => Promise<void>

  private menu = [
    {
      title: 'Manage Businesses',
      icon: 'business',
      activate: () => { this.setSelectedComponent(EntityManagement) },
      testTag: 'manage-business-nav'
    }
  ]

  async mounted () {
    this.setSelectedComponent(EntityManagement)
    const featureHide = ConfigHelper.getValue('VUE_APP_FEATURE_HIDE')
    if (!featureHide || !featureHide.USER_MGMT) {
      this.menu.push({
        title: 'Manage Team',
        icon: 'group',
        activate: () => { this.setSelectedComponent(UserManagement) },
        testTag: 'manage-teams-nav'
      })
    }

    // Check for existing state, and if not tell store to update
    if (!this.userProfile) {
      this.getUserProfile('@me')
    }

    if (!this.currentOrganization) {
      await this.syncOrganizations()
    }

    // Check the current user's team status
    // TODO: For now this means checking their single team, later it will mean checking the active team.
    this.redirectBasedOnTeamStatus()
  }

  setSelectedComponent (selectedComponent: VueConstructor) {
    this.selectedComponent = selectedComponent
  }

  private redirectBasedOnTeamStatus (): void {
    // If user is pending approval by an admin, redirect to pending approval page
    if (this.myOrgMembership && this.myOrgMembership.membershipStatus === MembershipStatus.Pending) {
      this.$router.push(`/pendingapproval/${this.currentOrganization.name}`)
    }

    // If user is not an active member of a team at all, redirect to create team page
    if (!this.myOrgMembership) {
      this.$router.push('/createteam')
    }
  }
}
</script>
