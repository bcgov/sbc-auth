/* eslint-disable no-console */
<template>
  <v-container class="p-0">
    <div class="users_list">
      <template v-if="createdUsers.length">
        <p>
          {{createdUsers.length}} Team Member(s) have been provisioned temporary passwords to login and access this account.
        </p>
        <v-card
          flat
          class="user-success-card my-4"
          v-if="createdUsers.length"
        >
          <v-card-text>
            <p>
              <strong>Added Team Member(s) Credentials</strong>
            </p>
            <ul>
              <li v-for="user in createdUsers" :key="user.username">
                {{ user.username }} / {{ user.password }}
              </li>
            </ul>
          </v-card-text>
        </v-card>
      </template>
      <!-- Failed Users List -->
      <template v-if="failedUsers.length">
        <p>
          {{failedUsers.length}} Team Member(s) have been failed to add, please check the list below
        </p>
        <v-card
          flat
          class="user-failed-card my-4"
          v-if="failedUsers.length"
        >
          <v-card-text>
            <p>
              <strong>Failed Team Member(s) </strong>
            </p>
            <ul>
              <li v-for="user in failedUsers" :key="user.username">
                <strong>{{ user.username }}</strong> : "{{ user.error }}"
              </li>
            </ul>
          </v-card-text>
        </v-card>
      </template>
      <div class="url">
        <p>
          <strong>Login URL</strong>
        </p>
        <ul>
          <li>
            {{ loginUrl}}
          </li>
        </ul>
      </div>
    </div>
  </v-container>
</template>

<script lang="ts">
import { AddUserBody, BulkUsersFailed, BulkUsersSuccess } from '@/models/Organization'
import { Component, Emit, Vue } from 'vue-property-decorator'
import { IdpHint, Pages } from '@/util/constants'
import { mapActions, mapMutations, mapState } from 'vuex'
import ConfigHelper from '@/util/config-helper'
import OrgModule from '@/store/modules/org'

@Component({
  computed: {
    ...mapState('org', [
      'createdUsers',
      'failedUsers'
    ])
  }
})
export default class AddUsersSuccess extends Vue {
  private readonly createdUsers!: BulkUsersSuccess[]
  private readonly failedUsers!: BulkUsersFailed[]
  private loginUrl: string = ConfigHelper.getSelfURL() + `/${Pages.SIGNIN}/${IdpHint.BCROS}`

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

  .user-success-card {
    background-color: $successCardBg !important;
    border-color: $successCardBg !important;
  }

  .user-failed-card {
    background-color: $errorCardBg !important;
    border-color: $errorCardBg !important;
  }

</style>
