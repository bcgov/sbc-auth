<template>
  <v-alert
    class="px-8 py-7"
    :icon="false"
    prominent
    type="error"
  >
    <div class="account-alert">
      <div class="account-alert-inner">
        <v-icon
          large
        >
          mdi-alert-circle-outline
        </v-icon>
        <div
          class="account-alert__info ml-7"
        >
          <div class="font-weight-bold">
            Account Deactivated
          </div>
        </div>
        <div
          class="account-alert__date"
        >
          {{ deactivatedDate }}
        </div>
      </div>
    </div>
  </v-alert>
</template>

<script lang="ts">
import { State } from 'pinia-class'
import { Component, Vue } from 'vue-property-decorator'
import CommonUtils from '@/util/common-util'
import { Organization } from '@/models/Organization'
import { useOrgStore } from '@/stores/org'

@Component
export default class AccountInActiveAlert extends Vue {
  @State(useOrgStore) private currentOrganization!: Organization
  private formatDate = CommonUtils.formatDisplayDate

  get deactivatedDate () {
    return (this.currentOrganization?.modified)
      ? this.formatDate(new Date(this.currentOrganization.modified)) : ''
  }
}
</script>

<style lang="scss" scoped>
  .account-alert-inner {
    display: flex;
    flex-direction: row;
    align-items: center;
  }

  .account-alert__info {
    flex: 1 1 auto;
  }

  .account-alert__date {
    flex: 0 0 auto;
  }

  .vertical-line {
  margin: 0 2em;
  border-left: solid;
  border-width: 0.125em;
  }

</style>
