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
import { mapActions, mapState } from 'vuex'
import ConfigHelper from '@/util/config-helper'
import EntityManagement from '@/views/management/EntityManagement.vue'
import ManagementMenu from '@/components/auth/ManagementMenu.vue'
import { Organization } from '@/models/Organization'
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
    ...mapState('user', ['userProfile'])
  },
  methods: {
    ...mapActions('user', ['getUserProfile']),
    ...mapActions('org', ['syncOrganizations'])
  }
})
export default class Dashboard extends Vue {
  private selectedComponent = null
  private readonly userProfile!: User
  private readonly getUserProfile!: (identifier: string) => User
  private readonly syncOrganizations!: () => Organization[]

  private menu = [
    {
      title: 'Manage Businesses',
      icon: 'business',
      activate: () => { this.setSelectedComponent(EntityManagement) },
      testTag: 'manage-business-nav'
    }
  ]

  mounted () {
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

    // Always pull organization list
    this.syncOrganizations()
  }

  setSelectedComponent (selectedComponent: VueConstructor) {
    this.selectedComponent = selectedComponent
  }
}
</script>
