<template>
  <div class="toolbar-container">
    <v-toolbar dark flat color="navBg">
      <v-toolbar-title>
        <router-link to="/home" color="#ffffff">Cooperatives Online</router-link>
      </v-toolbar-title>
      <v-toolbar-items flat>
        <v-btn color="navBg" to="/main/business">Manage Businesses</v-btn>
        <v-menu open-on-hover offset-y transition="slide-y-transition">
          <template v-slot:activator="{ on }">
            <v-btn color="navBg" v-on="on">
              Menu Item
              <v-icon small class="ml-2">mdi-chevron-down</v-icon>
            </v-btn>
          </template>
          <v-list dark dense flat color="navMenuBg">
            <v-list-item>
              <v-list-item-title>Item 1</v-list-item-title>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Item 1</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </v-toolbar-items>
    </v-toolbar>
    <!--
    <v-container class="pt-0 pb-0">
      <div v-if="currentOrganization" class="team-name">Cooperatives Online</div>
      <nav>
        <ul class="pl-0">
          <li v-for="(item, i) in menu"
            :key="i">
            <v-btn large text color="#495057" :to="item.path" :data-test="item.testTag">{{ item.title }}</v-btn>
          </li>
        </ul>
      </nav>
    </v-container>
    -->
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import OrgModule from '@/store/modules/org'
import { Organization } from '@/models/Organization'
import { User } from '@/models/user'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'
import { mapState } from 'vuex'

@Component({
  name: 'ManagementMenu',
  computed: {
    ...mapState('org', ['currentOrganization'])
  }
})
export default class ManagementMenu extends Vue {
  @Prop() menu
  private orgStore = getModule(OrgModule, this.$store)
  private userStore = getModule(UserModule, this.$store)
  private readonly currentOrganization!: Organization
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  .v-toolbar__title {
    margin-right: 1rem;
    font-size: 1rem;
    font-weight: 700;

    a {
      text-decoration: none;
      color: #ffffff;
    }
  }

  ::v-deep .v-toolbar__content {
    max-width: 1248px;
    margin: 0 auto;
  }

  .v-btn {
    box-shadow: none !important;
    font-size: 1rem;
    font-weight: 400;
  }
</style>
