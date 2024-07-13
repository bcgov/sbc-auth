<template>
  <v-card>
    <v-card-title class="card-title">
      <v-icon
        class="pr-5"
        color="link"
        left
      >
        mdi-file-document
      </v-icon>
      Short Name Refund
    </v-card-title>
    <v-card-text class="d-flex justify-space-between align-center card-content mt-4">
      <span>No refund initiated. SBC Finance can initiate refund if a CAS supplier number is created for the short name.</span>
      <v-btn
        class="mt-0 font-weight-regular"
        color="primary"
        outlined
        dark
        large
        :unsettledAmount="unsettledAmount"
        :shortNameDetails="shortNameDetails"
        @click="initiateRefund"
      >
        Initiate Refund
      </v-btn>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import { DEFAULT_DATA_OPTIONS } from '@/components/datatable/resources'
import _ from 'lodash'

export default defineComponent({
  name: 'ShortNameRefund',
  props: {
    shortNameDetails: {
      type: Object,
      default: () => ({})
    },
    unsettledAmount: {
      type: String,
      default: ''
    }
  },
  setup (props, { root }) {
    const state = reactive({
      actionDropdown: [],
      isShortNameLinkingDialogOpen: false,
      eftShortNameSummary: {},
      results: [],
      totalResults: 0,
      filters: {
        pageNumber: 1,
        pageLimit: 5
      },
      loading: false,
      options: _.cloneDeep(DEFAULT_DATA_OPTIONS),
      expanded: []
    })

    const isLinked = computed<boolean>(() => {
      return state.totalResults > 0 || state.loading
    })

    function initiateRefund () {
      root.$router?.push({
        name: 'shortnamerefund',
        query: {
          shortNameDetails: JSON.stringify(props.shortNameDetails),
          unsettledAmount: props.unsettledAmount
        }
      })
    }

    return {
      ...toRefs(state),
      state,
      isLinked,
      initiateRefund,
      formatCurrency: CommonUtils.formatAmount,
      formatAccountDisplayName: CommonUtils.formatAccountDisplayName
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
@import '@/assets/scss/actions.scss';
@import '@/assets/scss/ShortnameTables.scss';

.card-title {
  background-color: $app-lt-blue;
  justify-content: left;
  height: 75px;
  font-weight: bold;
  font-size: 1.125rem;

  .v-icon {
    font-size: 36px;
  }
}

.base-table__item-row-green {
  background-color: $table-green !important;
}

::v-deep {
  .base-table__item-cell {
    padding: 16px 0 16px 0
  }

  // Remove border for rows that are expanded with additional information
  tr:has(+ tr.expanded-item-row) td {
    border-bottom: none !important;
  }
}

.unlink-action-btn {
  border-radius: 4px !important;
}

.expanded-item-row {
  td {
    .expanded-item {
      display: grid;
      max-width: 80%;
      padding: 5px 0px 0px 0px;
      font-size: 16px;
      grid-template-columns: 35px 1fr;
      align-items: start;

      .v-icon {
        justify-content: left;
        grid-column: 1;
        padding-right: 4px !important;
        margin-right: 0px !important;
      }
    }

    .alert-item {
      .v-icon {
        color: $app-alert-orange;
      }
    }
  }
}
</style>
