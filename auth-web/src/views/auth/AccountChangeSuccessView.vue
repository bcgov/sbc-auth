<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" sm="6" class="text-center">
        <v-icon size="42" color="grey darken-3" class="mb-6">mdi-check</v-icon>
        <h1 class="mb-5">{{$t('bcscAccountChangeSuccessTitle')}}</h1>
        <p class="mb-9">{{$t('bcscAccountChangeSuccessSubtext')}}</p>
        <div>
          <v-btn large color="primary" @click="goTo('account-info')">
            <strong>View Account</strong>
          </v-btn>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component } from 'vue-property-decorator'
import { Organization } from '@/models/Organization'
import { Pages } from '@/util/constants'
import Vue from 'vue'
import { mapState } from 'vuex'

@Component({
  computed: {
    ...mapState('org', ['currentOrganization'])
  }
})
export default class AccountChangeSuccessView extends Vue {
  protected readonly currentOrganization!: Organization

  private goTo (page) {
    switch (page) {
      case 'home': this.$router.push('/')
        break
      case 'team-members': this.$router.push(`/${Pages.MAIN}/${this.currentOrganization.id}/settings/team-members`)
        break
      case 'account-info': this.$router.push(`/${Pages.MAIN}/${this.currentOrganization.id}/settings/account-info`)
        break
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";

  .container {
    padding-top: 3rem;
    padding-bottom: 3rem;
  }
</style>
