/* eslint-disable no-console */
<template>
  <v-container class="pt-1 text-left">

    <p class="mb-8" v-if="!createdUsers.length">
      {{ failedUsers.length }} {{ failedUsers.length > 1 ? 'Team Members' : 'Team Member' }} could not be added to this account.
    </p>

    <div class="mb-8" v-if="createdUsers.length">
      <p>{{ createdUsers.length }} {{ createdUsers.length > 1 ? 'Team Members have' : 'Team Member has' }} been added to this account.</p>
      <p>You will need to provide Team Members with their <strong>Username</strong>, <strong>Temporary Password</strong> and the <strong>Login Address</strong> to access this account.</p>
    </div>

    <div class="mb-3">
      <strong class="subtitle-1 font-weight-bold">Team Members</strong>
    </div>

      <template v-if="createdUsers.length">
        <v-list dense class="pt-0 pb-0">
          <template v-for="user in createdUsers">
            <v-divider class="mt-1 mb-1" :key="user"></v-divider>
            <v-list-item :key="user.username">
              <v-list-item-icon><v-icon color="success" class="mt-4">mdi-check</v-icon></v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title class="d-flex justify-start">
                  <div class="username">
                    <div class="caption">
                      Username
                    </div>
                    <div class="font-weight-bold">
                      {{ user.username }}
                    </div>
                  </div>
                  <div>
                    <div class="caption">
                      Temporary Password
                    </div>
                    <div class="font-weight-bold">
                      {{ user.password }}
                    </div>
                  </div>
                  </v-list-item-title>
                <!--
                <v-list-item-subtitle>Temporary Password: {{ user.password }}</v-list-item-subtitle>
                -->
              </v-list-item-content>
            </v-list-item>
          </template>
        </v-list>
        <!--
        <li class="d-flex justify-start pa-4" v-for="user in createdUsers" :key="user.username">
          <v-icon color="success" class="mr-5">mdi-check</v-icon>
          <div>
            <div class="caption">Username / Password</div>
            <div><strong>{{ user.username }} / {{ user.password }}</strong></div>
          </div>
        </li>
        -->
      </template>

      <template v-if="failedUsers.length">
        <v-list dense class="pt-0 pb-0">
          <template v-for="user in failedUsers">
            <v-divider class="mt-1 mb-1" :key="user"></v-divider>
            <v-list-item :key="user.username">
              <v-list-item-icon><v-icon color="error" class="mt-4">mdi-alert-circle-outline</v-icon></v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title class="d-flex justify-start error--text">
                  <div class="username">
                    <div class="caption">
                      Username
                    </div>
                    <div class="font-weight-bold">
                      {{ user.username }}
                    </div>
                  </div>
                  <div>
                    <div class="caption">
                      Error Message
                    </div>
                    <div class="font-weight-bold">
                      {{ user.error }}
                    </div>
                  </div>
                </v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </template>
        </v-list>
      </template>

      <!-- Failed Users List -->
      <!--
      <template v-if="failedUsers.length">
        <p>{{ failedUsers.length }} {{ failedUsers.length > 1 ? 'Team Members' : 'Team Member' }} could not be added to this account.</p>
        <div>
          <ul class="team-member__list">
            <li class="d-flex justify-start pa-4" v-for="user in failedUsers" :key="user.username">
              <v-icon color="error" class="mr-5">mdi-alert-circle-outline</v-icon>
              <div>
                <div class="caption">Username / Error Message</div>
                <div><strong>{{ user.username }}</strong> ({{ user.error }})</div>
              </div>
            </li>
          </ul>
        </div>
      </template>
      -->

      <!-- Login Address -->
      <div class="mt-6" v-if="createdUsers.length">
        <strong class="subtitle-1 font-weight-bold">Login Address</strong>
        <v-list dense class="mt-1 pt-0 pb-0">
          <v-list-item>
            <v-list-item-icon>
              <v-icon>mdi-arrow-right</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              {{ loginUrl }}
            </v-list-item-content>
          </v-list-item>
        </v-list>
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

  .section-title {
    font-size: 1.125rem;
  }

  .username {
    flex-basis: 45%;
    text-align: left;
  }
</style>
