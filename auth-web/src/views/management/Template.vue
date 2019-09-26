<template>
  <v-container class="view-container">
    <ManagementMenu :menu="menu" />
    <article class="view-container__content">
      <component :is="selectedComponent" />
    </article>
  </v-container>
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
    this.setSelectedComponent(UserManagement)
  }

  setSelectedComponent (selectedComponent: VueConstructor) {
    this.selectedComponent = selectedComponent
  }
}
</script>

<style lang="scss" scoped>
  .view-container {
    display: flex;
    flex-direction: row;
  }

  .view-container__content {
    flex: 1 1 auto;
  }

  article {
    margin-left: 1.5rem;
    padding: 0;
  }

  aside {
    margin: 0;
  }
</style>
