<template>
  <div class="d-flex mt-5 ml-5">
    <ManagementMenu :menu="menu" />
    <div class="content ml-5">
      <component :is="selectedComponent" />
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import ManagementMenu from '../../components/auth/ManagementMenu.vue'
import EntityManagement from './EntityManagement.vue'
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
    },
    {
      title: 'Manage Teams',
      icon: 'group',
      activate: () => { this.setSelectedComponent(UserManagement) }
    }
  ]

  mounted () {
    this.setSelectedComponent(EntityManagement)
  }

  setSelectedComponent (selectedComponent: VueConstructor) {
    this.selectedComponent = selectedComponent
  }
}
</script>

<style lang="scss">

.content {
  width: 80%
}
</style>
