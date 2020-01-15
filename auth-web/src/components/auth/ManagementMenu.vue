<template>
  <div class="toolbar-container">
    <v-toolbar dark flat color="navBg">
        <v-toolbar-title>Cooperatives Online</v-toolbar-title>
        <v-toolbar-items flat>
          <v-btn link color="primary" to="/main/business">Manage Businesses</v-btn>
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

  ul {
    list-style-type: none;
  }

  .team-toolbar {
    background-color: #ffffff;
  }

  .team-toolbar .container {
    display: flex;
    flex-direction: row;
    align-items: center;
    height: 4.5rem;
  }

  .team-toolbar .team-name {
    margin-right: 1.5rem;
    color: $gray7;
    letter-spacing: -0.02rem;
    font-size: 1.125rem;
  }

  .team-toolbar nav > ul > li {
    display: inline-block;
  }

  .v-toolbar__title {
    margin-right: 1rem;
    font-size: 1rem;
    font-weight: 700;
  }

  ::v-deep .v-toolbar__content {
    max-width: 1248px;
    margin: 0 auto;
  }

  .v-btn {
    box-shadow: none !important;
    font-weight: 700;
  }
</style>
