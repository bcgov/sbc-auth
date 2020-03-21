/* eslint-disable no-console */
<template>
  <v-container class="p-0">
    <div class="users_list">
      <p>
        {{createdUsers.length}} Team Members have been provisioned temporary passwords to login and access this account.
      </p>
      <p>
        <b>Team Members Credentials</b>
      </p>
      <ul>
        <li v-for="user in createdUsers" :key="user.username">
          {{ user.username }} / {{ user.password }}
        </li>
      </ul>
      <div class="url">
        <p>
          <b>Login URL</b>
        </p>
        <ul>
          <li>
            {{ loginUrl}}
          </li>
        </ul>
      </div>
     <!-- <v-btn icon class="mt-3 ml-1"
      @click="close()">
    </v-btn> -->
      </div>
    </v-container>
</template>

<script lang="ts">
import { Component, Emit, Vue } from 'vue-property-decorator'
import { mapActions, mapMutations, mapState } from 'vuex'
import { AddUserBody } from '@/models/Organization'
import ConfigHelper from '@/util/config-helper'
import OrgModule from '@/store/modules/org'

@Component({
  computed: {
    ...mapState('org', ['createdUsers'])
  }
})
export default class AddUsersForm extends Vue {
  private readonly createdUsers!: AddUserBody[]
  private loginUrl: string = ConfigHelper.getSelfURL() + '/auth/signin/bcros'

  @Emit()
  private close () { }
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';
  .users_list {
    text-align: left
  }

  .url {
    margin-top: 10px;
  }

</style>
