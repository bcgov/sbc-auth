/* eslint-disable no-console */
<template>
  <v-container class="pt-1 text-left">
    <div class="mb-8" v-if="createdUsers.length">
      <p>
        A new temporary password has been created for user
        <strong>{{ createdUsers[0].username | filterLoginSource }}</strong>
      </p>
      <p>
        You will need to provide Team Members with their
        <strong>Username</strong>, <strong>Temporary Password</strong> and the
        <strong>Login Address</strong> to access this account.
      </p>
    </div>

    <div class="mb-3">
      <strong class="subtitle-1 font-weight-bold">Team Members</strong>
    </div>

    <template v-if="createdUsers.length">
      <v-list dense class="pt-0 pb-0">
        <template v-for="(user, index) in createdUsers">
          <v-divider class="mt-1 mb-1" :key="index"></v-divider>
          <v-list-item :key="user.username">
            <v-list-item-icon
              ><v-icon color="success" class="mt-4"
                >mdi-check</v-icon
              ></v-list-item-icon
            >
            <v-list-item-content>
              <v-list-item-title class="d-flex justify-start">
                <div class="username">
                  <div class="caption">
                    Username
                  </div>
                  <div class="font-weight-bold">
                    {{ user.username | filterLoginSource }}
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
            </v-list-item-content>
          </v-list-item>
        </template>
      </v-list>
    </template>
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
import { Component, Emit, Vue } from 'vue-property-decorator'
import { IdpHint, Pages } from '@/util/constants'
import { BulkUsersSuccess } from '@/models/Organization'
import ConfigHelper from '@/util/config-helper'
import { mapState } from 'vuex'

@Component({
  computed: {
    ...mapState('org', ['createdUsers', 'failedUsers'])
  },
  filters: {
    filterLoginSource (value: string) {
      return value.replace('bcros/', '')
    }
  }
})
export default class AddUsersSuccess extends Vue {
  private readonly createdUsers!: BulkUsersSuccess[]
  private loginUrl: string = ConfigHelper.getSelfURL() + `/${Pages.SIGNIN}/${IdpHint.BCROS}`

  @Emit()
  private close () {}
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
