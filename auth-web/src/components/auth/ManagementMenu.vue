<template>
  <v-navigation-drawer width="216">
    <v-list dense nav>
      <v-list-item small color="primary"
        v-for="(item, i) in menu"
        :key="i"
        @click="item.activate()">
        <v-list-item-icon>
          <v-icon>{{ item.icon }}</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title v-text="item.title"></v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator'

@Component({
  name: 'ManagementMenu'
})
export default class ManagementMenu extends Vue {
  @Prop()
  menu

  mini () {
    switch (this.$vuetify.breakpoint.name) {
      case 'xs': return true
      case 'sm': return true
      case 'md': return false
      case 'lg': return false
      case 'xl': return false
    }
  }
}
</script>

<style lang="scss">
  .v-navigation-drawer {
    background-color : transparent !important;
  }

  .v-navigation-drawer__border {
    display: none;
  }

  .v-list--nav {
    padding: 0;
  }
</style>
