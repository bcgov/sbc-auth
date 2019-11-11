<template>
  <div class="team-toolbar">
  <v-container class="pt-0 pb-0">
    <div class="team-name">Organization Name</div>
    <nav>
      <ul class="pl-0">
        <li v-for="(item, i) in menu"
          :key="i">
          <v-btn tile text color="#ffffff" @click="item.activate()">{{item.title}}</v-btn>
        </li>
      </ul>
    </nav>

  <!--
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
  -->
  </v-container>
  </div>
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

<style lang="scss" scoped>
  @import '../../assets/scss/theme.scss';

  ul {
    list-style-type: none;
  }

  .team-toolbar {
    color: #ffffff;
    background-color: $BCgovBlue4;
  }

  .team-toolbar .container {
    display: flex;
    flex-direction: row;
    align-items: center;
  }

  .team-toolbar .team-name {
    margin-right: 1.25rem;
    font-weight: 700;
  }

  .team-toolbar nav > ul > li {
    display: inline-block;
  }

  .v-btn {
    height: 4.5rem !important;
    letter-spacing: 0.01rem;
    font-weight: 400;
  }
</style>
