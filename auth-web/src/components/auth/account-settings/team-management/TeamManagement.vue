<template>
  <v-container class="team-mgmt-container">
    <UserManagement />
  </v-container>
</template>

<script lang="ts">
import { Component, Mixins, Prop } from 'vue-property-decorator'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import UserManagement from '@/components/auth/account-settings/team-management/UserManagement.vue'
import { mapState } from 'pinia'
import { useOrgStore } from '@/stores/org'

@Component({
  components: {
    UserManagement
  },
  computed: {
    ...mapState(useOrgStore, [
      'currentMembership',
      'currentOrganization'
    ])
  },
  methods: {

  }
})
export default class TeamManagement extends Mixins(NextPageMixin) {
  @Prop({ default: '' }) private orgId: string
}
</script>

<style lang="scss" scoped>
  .team-mgmt-container {
    overflow: hidden;
  }
</style>
