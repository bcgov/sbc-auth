<template>
  <v-container>
    <header class="view-header align-center">
      <h2 class="view-header__title">Transactions</h2>
      <div class="view-header__actions">
        <v-btn color="primary" data-test="export-button">
          <span>Export</span>
        </v-btn>
      </div>
    </header>
    <TransactionsDataTable
    ></TransactionsDataTable>
  </v-container>
</template>

<script lang="ts">
import { ActiveUserRecord, Member, MembershipStatus, MembershipType, Organization, PendingUserRecord, UpdateMemberPayload } from '@/models/Organization'
import { Component, Mixins, Prop, Vue, Watch } from 'vue-property-decorator'
import { Transaction, TransactionListResponse } from '@/models/transaction'
import { mapActions, mapState } from 'vuex'
import { Business } from '@/models/business'
import ConfigHelper from '@/util/config-helper'
import { Event } from '@/models/event'
import { EventBus } from '@/event-bus'
import { Invitation } from '@/models/Invitation'
import ModalDialog from '@/components/auth/ModalDialog.vue'
import OrgModule from '@/store/modules/org'
import { SessionStorageKeys } from '@/util/constants'
import TransactionsDataTable from '@/components/auth/TransactionsDataTable.vue'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    TransactionsDataTable,
    ModalDialog
  },
  computed: {
  },
  methods: {
    ...mapActions('org', [
      'getTransactionList'
    ])
  }
})
export default class Transactions extends Vue {
  @Prop({ default: '' }) private orgId: string;
}
</script>

<style lang="scss" scoped>
  .view-header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }

  ::v-deep {
    .v-data-table td {
      padding-top: 1rem;
      padding-bottom: 1rem;
      height: auto;
      vertical-align: top;
    }

    .v-list-item__title {
      display: block;
      font-weight: 700;
    }

    .v-badge--inline .v-badge__wrapper {
      margin-left: 0;

      .v-badge__badge {
        margin-right: -0.25rem;
        margin-left: 0.25rem;
      }
    }
  }

  .notify-checkbox {
    justify-content: center;

    ::v-deep {
      .v-input__slot {
        margin-bottom: 0 !important;
      }
    }
  }
</style>
