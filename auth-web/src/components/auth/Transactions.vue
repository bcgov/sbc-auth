<template>
  <v-container>
    <header class="view-header mb-6">
      <h2 class="view-header__title">Transactions</h2>
    </header>
    <TransactionsDataTable></TransactionsDataTable>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import TransactionsDataTable from '@/components/auth/TransactionsDataTable.vue'

@Component({
  components: {
    TransactionsDataTable
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
