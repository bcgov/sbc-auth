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
    <v-card-text
      v-if="!state.results.length"
      class="d-flex justify-space-between align-center card-content mt-4"
    >
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
    <v-card-text
      v-if="state.results.length"
      class="pa-0 linked-text"
    >
      <BaseVDataTable
        id="eft-transactions-table"
        ref="historyTable"
        class="transaction-list"
        itemKey="id"
        :setItems="state.results"
        :totalItems="state.totalResults"
        :setHeaders="headers"
        :pageHide="true"
        :hideFilters="true"
      >
        <template #item-slot-refundAmount="{ item }">
          <span>{{ formatCurrency(Number(item.refundAmount)) }}</span>
          <span
            class="view-refund-details"
            @click="viewRefundDetails(item.id)"
          >View Refund Detail</span>
        </template>
        <template #item-slot-actions="{ item, index }">
          <div
            :id="`action-menu-${index}`"
            class="mx-auto"
          >
            <v-btn
              v-if="isEftRefundApprover"
              small
              outlined
              color="primary"
              class="open-action-btn pr-4 pl-4 mr-3"
              :loading="loading"
              @click="declineRefund(item)"
            >
              <v-icon
                class="mr-2"
              >
                mdi-close
              </v-icon>
              Decline
            </v-btn>
            <v-btn
              v-if="isEftRefundApprover"
              small
              color="primary"
              class="open-action-btn pr-4 pl-4"
              :loading="loading"
              @click="approveRefund(item)"
            >
              <v-icon
                class="mr-2"
              >
                mdi-check
              </v-icon>
              Approve
            </v-btn>
          </div>
        </template>
      </BaseVDataTable>
    </v-card-text>
    <ModalDialog
      ref="confirmationDialog"
      max-width="720"
      :show-icon="false"
      :showCloseIcon="true"
      dialog-class="confirmation-dialog"
      title="Decline Refund Request?"
    >
      <template #text>
        <p class="pt-4">
          By declining the request, the amount will remain unsettled in the short name.
        </p>
        <v-text-field
          v-model="declineReason"
          filled
          label="Reasons for declining (Optional)"
          persistent-hint
        />
      </template>
      <template #actions>
        <div class="d-flex align-center justify-center w-100 h-100 ga-3">
          <v-btn
            outlined
            large
            depressed
            class="mr-3"
            color="primary"
            data-test="btn-cancel-confirmation-dialog"
            @click="dialogCancel"
          >
            Cancel
          </v-btn>
          <v-btn
            large
            depressed
            class="font-weight-bold btn-dialog"
            data-test="btn-confirm-confirmation-dialog"
            color="primary"
            @click="dialogDecline"
          >
            Decline
          </v-btn>
        </div>
      </template>
    </ModalDialog>
  </v-card>
</template>

<script lang="ts">
import { EFTRefundType, Role, ShortNameHistoryType } from '@/util/constants'
import { Ref, computed, defineComponent, reactive, ref, toRefs, watch } from '@vue/composition-api'
import { BaseVDataTable } from '@/components'
import CommonUtils from '@/util/common-util'
import { DEFAULT_DATA_OPTIONS } from '@/components/datatable/resources'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import PaymentService from '@/services/payment.services'
import _ from 'lodash'
import { useUserStore } from '@/stores/user'

export default defineComponent({
  name: 'ShortNameRefund',
  components: { BaseVDataTable, ModalDialog },
  props: {
    shortNameDetails: {
      type: Object,
      default: () => ({
        shortName: null
      })
    },
    unsettledAmount: {
      type: String,
      default: ''
    }
  },
  setup (props, { root }) {
    const userStore = useUserStore()
    const state = reactive({
      declineReason: '',
      actionDropdown: [],
      isShortNameLinkingDialogOpen: false,
      eftShortNameSummary: {},
      results: [],
      totalResults: 1,
      filters: {
        pageNumber: 1,
        pageLimit: 5
      },
      loading: false,
      options: _.cloneDeep(DEFAULT_DATA_OPTIONS),
      expanded: [],
      currentEftRefund: null,
      isEftRefundApprover: computed(() => userStore.currentUser.roles.includes(Role.EftRefundApprover))
    })
    const confirmationDialog: Ref<InstanceType<typeof ModalDialog>> = ref(null)
    const headers = [
      {
        col: 'createdName',
        hasFilter: false,
        width: '300px',
        value: 'Initiated by'
      },
      {
        col: 'casSupplierNumber',
        hasFilter: false,
        width: '210px',
        value: 'Supplier Record Number'
      },
      {
        col: 'refundAmount',
        hasFilter: false,
        width: '260px',
        value: 'Refund Amount'
      },
      {
        col: 'actions',
        hasFilter: false,
        value: 'Actions',
        width: '200px'
      }
    ]

    async function approveRefund (item) {
      const shortNameRefund = {
        status: EFTRefundType.APPROVED
      }
      try {
        await PaymentService.patchEFTRefund(item.id, shortNameRefund)
        await loadTransactions(props.shortNameDetails.id)
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Failed to approve refund.', error)
      }
    }

    function declineRefund (item) {
      state.currentEftRefund = item
      confirmationDialog.value.open()
    }

    async function dialogDecline () {
      const shortNameRefund = {
        status: EFTRefundType.DECLINED,
        decline_reason: state.declineReason
      }
      try {
        await PaymentService.patchEFTRefund(state.currentEftRefund.id, shortNameRefund)
        await loadTransactions(props.shortNameDetails.id)
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Failed to decline refund.', error)
      }
      confirmationDialog.value.close()
      state.currentEftRefund = null
    }

    watch(() => props.shortNameDetails, () => {
      return loadTransactions(props.shortNameDetails.id)
    }, { immediate: true, deep: true })

    async function loadTransactions (shortnameId: string): Promise<void> {
      try {
        state.loading = true
        const response = await PaymentService.getEFTShortnameHistory(shortnameId, state.filters)
        if (response?.data) {
          const filteredResults = response.data.items.filter(
            (item) => item.transactionType === ShortNameHistoryType.SN_REFUND_PENDING_APPROVAL
          )

          for (const item of filteredResults) {
            const eftRefundId = item.eftRefundId
            const eftRefund = await PaymentService.getEFTRefund(eftRefundId)
            state.results.push(eftRefund.data)
          }

          state.totalResults = filteredResults.length
        } else {
          throw new Error('No response from getEFTTransactions')
        }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Failed to getEFTTransactions list.', error)
      }
      state.loading = false
    }

    function dialogCancel () {
      confirmationDialog.value.close()
    }

    function viewRefundDetails (id: string) {
      if (!id) return
      root.$router?.push({
        name: 'shortnamerefund',
        params: {
          eftRefundId: id
        }
      })
    }

    function initiateRefund () {
      root.$router?.push({
        name: 'shortnamerefund',
        params: {
          shortNameId: props.shortNameDetails.id
        }
      })
    }

    return {
      ...toRefs(state),
      state,
      headers,
      confirmationDialog,
      approveRefund,
      declineRefund,
      dialogDecline,
      dialogCancel,
      initiateRefund,
      viewRefundDetails,
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
  // Remove border for rows that are expanded with additional information
  tr:has(+ tr.expanded-item-row) td {
    border-bottom: none !important;
  }
}

.unlink-action-btn {
  border-radius: 4px !important;
}

.view-refund-details {
  color: var(--v-primary-base);
  text-decoration: underline;
  font-weight: 100;
  display: block;
  cursor: pointer;
}

.w-100 {
  width: 100%;
}

.h-100 {
  height: 100%;
}

.ga-3 {
  gap: 12px;
}

.open-action-btn {
  box-shadow: none;
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
