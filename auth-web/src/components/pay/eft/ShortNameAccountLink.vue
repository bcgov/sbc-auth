<template>
  <v-card v-if="shortNameDetails.shortName">
    <ShortNameLinkingDialog
      :isShortNameLinkingDialogOpen="isShortNameLinkingDialogOpen"
      :selectedShortName="eftShortNameSummary"
      @close-short-name-linking-dialog="closeShortNameLinkingDialog"
      @on-link-account="onLinkAccount"
    />
    <v-card-title class="card-title">
      <v-icon
        class="pr-5"
        color="link"
        left
      >
        mdi-bank-transfer
      </v-icon>
      Accounts Linked to {{shortNameDetails.shortName}}
    </v-card-title>

    <v-card-text
      v-if="isLinked"
      class="pa-5 linked-text"
    >
      <v-btn
        id="link-shortname-btn"
        color="primary"
        outlined
        dark
        large
        class="mt-0 mr-4 font-weight-regular"
        @click="openAccountLinkingDialog()"
      >
        + Link a New Account
      </v-btn>
      <BaseVDataTable
          id="eft-account-linking-table"
          class="eft-account-links-list pt-2"
          itemKey="id"
          :loading="state.loading"
          loadingText="Loading Records..."
          noDataText="No Records."
          :setItems="state.results"
          :setHeaders="headers"
          :setTableDataOptions="state.options"
          :totalItems="state.totalResults"
          :filters="state.filters"
          :pageHide="true"
          :hideFilters="true"
          :hasTitleSlot="false"
          :highlight-index="highlightIndex"
          highlight-class="base-table__item-row-green"
          @update-table-options="state.options = $event"
      >
        <template #item-slot-linkedAccount="{ item }">
          <span>{{ formatAccountDisplayName(item) }}</span>
        </template>
        <template #item-slot-amountOwing="{ item }">
          <span>{{ formatCurrency(item.amountOwing) }}</span>
        </template>
        <template #item-slot-actions="{ item, index }">
          <div
              :id="`action-menu-${index}`"
              class="new-actions mx-auto"
          >
            <v-btn
                small
                color="primary"
                min-width="5rem"
                min-height="2rem"
                class="open-action-btn"
            >
              Cancel Payment
            </v-btn>
            <span class="more-actions">
            <v-menu
                v-model="actionDropdown[index]"
                :attach="`#action-menu-${index}`"
                offset-y
                nudge-left="74"
            >
              <template #activator="{ on }">
                <v-btn
                    small
                    color="primary"
                    min-height="2rem"
                    class="more-actions-btn"
                    v-on="on"
                >
                  <v-icon>{{ actionDropdown[index] ? 'mdi-menu-up' : 'mdi-menu-down' }}</v-icon>
                </v-btn>
              </template>
              <v-list>
                <v-list-item
                    class="actions-dropdown_item"
                    data-test="link-account-button"
                >
                  <v-list-item-subtitle>
                    <span class="pl-1 cursor-pointer">Cancel payment and remove linkage</span>
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-menu>
          </span>
          </div>
        </template>
      </BaseVDataTable>
    </v-card-text>

    <v-card-text
      v-else
      class="d-flex justify-space-between pa-5 unlinked-text"
    >
      This short name is not linked with an account.
      <v-btn
        id="link-shortname-btn"
        color="primary"
        @click="openAccountLinkingDialog()"
      >
        Link to Account
      </v-btn>
    </v-card-text>
  </v-card>
</template>
<script lang="ts">

import { BaseVDataTable } from '@/components'
import { DEFAULT_DATA_OPTIONS } from '@/components/datatable/resources'
import CommonUtils from '@/util/common-util'
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import PaymentService from '@/services/payment.services'
import ShortNameLinkingDialog from '@/components/pay/eft/ShortNameLinkingDialog.vue'
import _ from 'lodash'

export default defineComponent({
  name: 'ShortNameAccountLinkage',
  components: { BaseVDataTable, ShortNameLinkingDialog },
  props: {
    shortNameDetails: {
      type: Object,
      default: () => ({})
    },
    highlightIndex: {
      type: Number,
      default: -1
    }
  },
  emits: ['on-link-account'],
  setup (props, { emit }) {
    const headers = [
      {
        col: 'linkedAccount',
        hasFilter: false,
        minWidth: '200px',
        value: 'Linked Account'
      },
      {
        col: 'accountBranch',
        hasFilter: false,
        minWidth: '200px',
        value: 'Branch'
      },
      {
        col: 'statementId',
        hasFilter: false,
        minWidth: '200px',
        value: 'Latest Statement Number'
      },
      {
        col: 'amountOwing',
        hasFilter: false,
        minWidth: '175px',
        value: 'Amount Owing'
      },
      {
        col: 'actions',
        hasFilter: false,
        value: 'Actions',
        minWidth: '150px'
      }
    ]

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
      options: _.cloneDeep(DEFAULT_DATA_OPTIONS)
    })

    const isLinked = computed<boolean>(() => {
      return state.totalResults > 0 || state.loading
    })

    const accountDisplayText = computed<string>(() => {
      return `${props.shortNameDetails.accountId} ${props.shortNameDetails.accountName}`
    })

    function openAccountLinkingDialog () {
      state.isShortNameLinkingDialogOpen = true
    }

    function closeShortNameLinkingDialog () {
      state.isShortNameLinkingDialogOpen = false
    }

    function onLinkAccount (account: any) {
      loadShortNameLinks()
      emit('on-link-account', account)
    }

    async function getEFTShortNameSummaries () {
      const filters = {
        filterPayload: {
          shortNameId: props.shortNameDetails.id
        }
      }
      const EFTShortNameSummaries = await PaymentService.getEFTShortNameSummaries(filters)
      if (EFTShortNameSummaries.data && EFTShortNameSummaries.data.items.length > 0) {
        state.eftShortNameSummary = EFTShortNameSummaries.data.items[0]
      }
    }

    async function loadShortNameLinks () {
      try {
        state.loading = true
        const response = await PaymentService.getEFTShortNameLinks(props.shortNameDetails.id)
        if (response?.data) {
          /* We use appendToResults for infinite scroll, so we keep the existing results. */
          state.results = response.data.items
          state.totalResults = response.data.items.length
        } else {
          throw new Error('No response from loadShortNameLinks')
        }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Failed to loadShortNameLinks list.', error)
      }
      state.loading = false
    }

    watch(() => props.shortNameDetails.id, () => {
      getEFTShortNameSummaries()
      loadShortNameLinks()
    })

    return {
      ...toRefs(state),
      state,
      headers,
      isLinked,
      accountDisplayText,
      openAccountLinkingDialog,
      closeShortNameLinkingDialog,
      onLinkAccount,
      getEFTShortNameSummaries,
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
}

</style>
