<template>
  <v-toolbar class="management-header">
    <span>Org Name</span>
  </v-toolbar>
  <!-- <v-navigation-drawer width="216">
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
  </v-navigation-drawer> -->
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

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
  @import "$assets/scss/theme.scss";

  .management-header {
    background-color: $BCgovBlue4 !important;
    max-height: 3.5em;
    color: white !important;
  }
</style>
