<template>
  <v-navigation-drawer
    value="true"
    mobile-break-point="960"
    class="ml-5"
    :mini-variant="mini()"
  >
    <v-list>
      <v-list-item
        v-for="(item, i) in menu"
        :key="i"
        @click="item.activate()">
        <v-icon>{{ item.icon }}</v-icon>&nbsp;&nbsp;
        <v-list-item-title v-text="item.title"></v-list-item-title>
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
</style>
