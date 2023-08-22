<template>
  <div class="team-toolbar">
    <v-container class="pt-0 pb-0">
      <div
        v-if="currentOrganization"
        class="team-name"
      >
        {{ currentOrganization.name }}
      </div>
      <nav>
        <ul class="pl-0">
          <li
            v-for="(item, i) in menu"
            :key="i"
          >
            <v-btn
              large
              text
              color="#495057"
              :to="item.path"
              :data-test="item.testTag"
            >
              {{ item.title }}
            </v-btn>
          </li>
        </ul>
      </nav>
    </v-container>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { Organization } from '@/models/Organization'
import { mapState } from 'pinia'
import { useOrgStore } from '@/store/org'

@Component({
  name: 'ManagementMenu',
  computed: {
    ...mapState(useOrgStore, ['currentOrganization'])
  }
})
export default class ManagementMenu extends Vue {
  @Prop() menu
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

  .v-btn {
    text-transform: uppercase;
    font-weight: 700
  }
</style>
