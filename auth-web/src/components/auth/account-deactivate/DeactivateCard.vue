import { AccessType } from '@/util/constants'
<template>
  <v-card>
    <v-card-title>
      When this account is deactivated.
    </v-card-title>

    <v-card-text>
      <div v-for="item in info" :key="item"  class="d-flex align-center">
        <div><v-icon color="error" class="mt-1 mr-4">mdi-alert-circle-outline</v-icon></div>
        <div><h4 class="font-weight-bold ">{{ item.text }}</h4>
          <p>{{ item.subtext }}</p>
        </div>

      </div>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { mapActions, mapMutations, mapState } from 'vuex'
import CommonUtils from '@/util/common-util'
import { FailedInvoice } from '@/models/invoice'
import { Organization } from '@/models/Organization'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'

@Component({
  computed: {
    ...mapState('org', [
      'currentOrganization'
    ])
  },
  methods: {
    ...mapActions('org', [
      'calculateFailedInvoices'
    ])
  }
})
export default class DeactivateCard {
  private info: Array<any> = [
    { text: 'All team members will be removed from this account.', 'subtext': 'Account Administrators and all other team members will no longer be able to access functionality related to this account.', 'type': 'BASIC' },
    { text: 'Business that are affiliated with this account will be removed.', 'subtext': 'All businesses that have been affiliated with this account will be removed.Passcode usec to affilate with business will reset and you will not be able to reuse the passcode.', 'type': 'BASIC' }

  ]
}
</script>

<style lang="scss" scoped>
@import "$assets/scss/theme.scss";

.suspended-info-card {
  border-color: $BCgovInputError !important;
  border-width: 2px !important;

  .sub-txt {
    font-size: .75rem;
  }
}
</style>
