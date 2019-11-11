<template>
  <v-app class="view-container">
    <ManagementMenu :menu="menu" />
    <article>
      <component :is="selectedComponent" />
    </article>
  </v-app>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
import EntityManagement from './EntityManagement.vue'
import ManagementMenu from '../../components/auth/ManagementMenu.vue'
import UserManagement from './UserManagement.vue'
import { VueConstructor } from 'vue'

@Component({
  name: 'Template',
  components: {
    ManagementMenu,
    EntityManagement,
    UserManagement
  }
})
export default class Dashboard extends Vue {
  private selectedComponent = null

  private menu = [
    {
      title: 'Manage Businesses',
      icon: 'business',
      activate: () => { this.setSelectedComponent(EntityManagement) }
    }
  ]

  mounted () {
    this.setSelectedComponent(EntityManagement)
    const featureHide = ConfigHelper.getValue('VUE_APP_FEATURE_HIDE')
    if (!featureHide || !featureHide.USER_MGMT) {
      this.menu.push({
        title: 'Manage Team',
        icon: 'group',
        activate: () => { this.setSelectedComponent(UserManagement) }
      })
    }
  }

  setSelectedComponent (selectedComponent: VueConstructor) {
    this.selectedComponent = selectedComponent
  }
}
</script>

<style lang="scss" scoped>
  .view-container {
    display: flex;
  }

  aside {
    margin: 0;
  }
</style>
