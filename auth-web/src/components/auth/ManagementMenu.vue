<template>
  <div class="team-toolbar">
  <v-container class="pt-0 pb-0">
    <div v-if="myOrg" class="team-name">{{ myOrg.name }}</div>
    <nav>
      <ul class="pl-0">
        <li v-for="(item, i) in menu"
          :key="i">
          <v-btn large text color="#495057" @click="item.activate()">{{ item.title }}</v-btn>
        </li>
      </ul>
    </nav>
  </v-container>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { mapActions, mapGetters, mapState } from 'vuex'
import OrgModule from '@/store/modules/org'
import { Organization } from '@/models/Organization'
import { User } from '@/models/user'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'

@Component({
  name: 'ManagementMenu',
  computed: {
    ...mapGetters('org', ['myOrg'])
  },
  methods: {
    ...mapActions('org', ['syncOrganizations'])
  }
})
export default class ManagementMenu extends Vue {
  @Prop() menu
  private orgStore = getModule(OrgModule, this.$store)
  private userStore = getModule(UserModule, this.$store)
  private readonly myOrg!: Organization
  private readonly syncOrganizations!: () => Organization[]

  async mounted () {
    await this.syncOrganizations()
    if (!this.myOrg) {
      this.$router.push({ path: '/createteam' })
    }
  }
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
