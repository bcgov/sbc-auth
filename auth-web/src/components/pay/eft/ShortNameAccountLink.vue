<template>
  <v-card v-if="shortNameDetails.shortName">
    <ShortNameLinkingDialog
      :isShortNameLinkingDialogOpen="isShortNameLinkingDialogOpen"
      :selectedShortName="eftShortNameSummary"
      @close-short-name-linking-dialog="closeShortNameLinkingDialog"
      @on-link-account="onLinkAccount"
    />
    <ModalDialog
      ref="confirmationDialog"
      max-width="720"
      :show-icon="false"
      :showCloseIcon="true"
      dialog-class="confirmation-dialog"
      :title="`${confirmDialogTitle}`"
    >
      <template #text>
        <p class="pt-4">
          {{ confirmDialogText }}
        </p>
      </template>
      <template #actions>
        <div class="d-flex justify-center dialog-button-container">
          <v-btn
            outlined
            large
            depressed
            class="mr-3"
            color="primary"
            data-test="btn-cancel-change-access-type-dialog"
            @click="dialogConfirmClose"
          >
            Cancel
          </v-btn>
          <v-btn
            large
            depressed
            class="font-weight-bold btn-dialog"
            data-test="btn-confirm-change-access-type-dialog"
            color="primary"
            @click="dialogConfirm"
          >
            Confirm
          </v-btn>
        </div>
      </template>
    </ModalDialog>
    <v-card-title class="card-title">
      <v-icon
        class="pr-5"
        color="link"
        left
      >
        mdi-bank-transfer
      </v-icon>
      Accounts Linked to {{ shortNameDetails.shortName }}
    </v-card-title>

    <v-card-text
      v-if="isLinked"
      class="pa-0 linked-text"
    >
      <v-btn
        id="link-shortname-btn"
        color="primary"
        outlined
        dark
        large
        class="mt-4 ml-4 font-weight-regular"
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
        :setExpanded="state.expanded"
        @update-table-options="state.options = $event"
      >
        <template #item-slot-linkedAccount="{ item }">
          <span>{{ formatAccountDisplayName(item) }}</span>
        </template>
        <template #item-slot-amountOwing="{ item }">
          <span>{{ formatCurrency(item.amountOwing) }}</span>
        </template>
        <template #expanded-item="{ item }">
          <tr class="expanded-item-row">
            <td
              :colspan="headers.length"
              class="pb-5 pl-0"
            >
              <span class="expanded-item scheduled-item">
                <v-icon>mdi-clock-outline</v-icon>
                {{ formatCurrency(item.amountOwing) }} will be applied to this account today at 5:00 p.m. PST or 6:00 p.m. PDT.
              </span>
            </td>
          </tr>
        </template>
        <template #item-slot-actions="{ item, index }">
          <div
            :id="`action-menu-${index}`"
            class="new-actions mx-auto"
          >
            <!-- Cancel Payment-->
            <template v-if="item.hasPendingPayment">
              <v-btn
                small
                color="primary"
                min-width="5rem"
                min-height="2rem"
                class="open-action-btn single-action-btn"
                :loading="loading"
                @click="showConfirmCancelPaymentModal(item)"
              >
                Cancel Payment
              </v-btn>
            </template>
            <!-- Apply Payments / Unlink Buttons -->
            <template v-else-if="showApplyPayment(item)">
              <v-btn
                small
                color="primary"
                min-width="5rem"
                min-height="2rem"
                class="open-action-btn"
                :loading="loading"
                @click="applyPayment(item)"
              >
                Apply Payments
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
                      :loading="loading"
                      v-on="on"
                    >
                      <v-icon>{{ actionDropdown[index] ? 'mdi-menu-up' : 'mdi-menu-down' }}</v-icon>
                    </v-btn>
                  </template>
                  <v-list>
                    <v-list-item
                      class="actions-dropdown_item"
                    >
                      <v-list-item-subtitle
                        @click="showConfirmUnlinkAccountModal(item)"
                      >
                        <span class="pl-1 cursor-pointer">Unlink Account</span>
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </span>
            </template>
            <!-- Unlink Account Button -->
            <template v-else>
              <v-btn
                small
                color="primary"
                min-width="5rem"
                min-height="2rem"
                class="open-action-btn single-action-btn"
                :loading="loading"
                @click="showConfirmUnlinkAccountModal(item)"
              >
                Unlink Account
              </v-btn>
            </template>
          </div>
        </template>
      </BaseVDataTable>
    </v-card-text>

    <v-card-text
      v-else
      class="d-flex justify-space-between pa-5 unlinked-text"
    >
      <span class="pt-1">
        This short name is not linked with an account.
      </span>
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

import { Ref, computed, defineComponent, reactive, ref, toRefs, watch } from '@vue/composition-api'
import { ShortNameLinkStatus, ShortNamePaymentActions } from '@/util/constants'
import { BaseVDataTable } from '@/components'
import CommonUtils from '@/util/common-util'
import { DEFAULT_DATA_OPTIONS } from '@/components/datatable/resources'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import PaymentService from '@/services/payment.services'
import ShortNameLinkingDialog from '@/components/pay/eft/ShortNameLinkingDialog.vue'
import { Vue } from 'vue-property-decorator'
import _ from 'lodash'

export default defineComponent({
  name: 'ShortNameAccountLinkage',
  components: { ModalDialog, BaseVDataTable, ShortNameLinkingDialog },
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
  emits: ['on-link-account', 'on-payment-action'],
  setup (props, { emit }) {
    const enum ConfirmationType {
      CANCEL_PAYMENT = 'cancelPayment',
      UNLINK_ACCOUNT = 'unlinkAccount'
    }
    const confirmationDialog: Ref<InstanceType<typeof ModalDialog>> = ref(null)
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
      confirmDialogTitle: '',
      confirmDialogText: '',
      confirmObject: undefined,
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

    const accountDisplayText = computed<string>(() => {
      return `${props.shortNameDetails.accountId} ${props.shortNameDetails.accountName}`
    })

    async function evaluateLinks () {
      let pending = state.results.filter(result =>
        result.statusCode === ShortNameLinkStatus.PENDING && result.amountOwing > 0
      )

      await Vue.nextTick()
      state.expanded = [...pending]
    }

    function openAccountLinkingDialog () {
      state.isShortNameLinkingDialogOpen = true
    }

    function closeShortNameLinkingDialog () {
      state.isShortNameLinkingDialogOpen = false
    }

    async function onLinkAccount (account: any) {
      await loadShortNameLinks()
      emit('on-link-account', account, state.results)
    }

    function showApplyPayment (item: any) {
      return props.shortNameDetails.creditsRemaining >= item.amountOwing
    }

    function dialogConfirm () {
      confirmationDialog.value.close()
      const confirmationType = state.confirmObject.type
      if (confirmationType === ConfirmationType.CANCEL_PAYMENT) {
        cancelPayment(state.confirmObject.item)
      } else if (confirmationType === ConfirmationType.UNLINK_ACCOUNT) {
        unlinkAccount(state.confirmObject.item)
      }
      resetConfirmationDialog()
    }

    function dialogConfirmClose () {
      confirmationDialog.value.close()
    }

    async function applyPayment (item) {
      state.loading = true
      try {
        await PaymentService.postShortnamePaymentAction(props.shortNameDetails.id,
          item.accountId, ShortNamePaymentActions.APPLY_CREDITS)
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('An errored occurred cancelling payments pending.', error)
      }
      this.$emit('on-payment-action')
      state.loading = false
    }

    function resetConfirmationDialog () {
      state.confirmDialogTitle = ''
      state.confirmDialogText = ''
      state.confirmObject = undefined
    }

    function showConfirmCancelPaymentModal (item) {
      state.confirmDialogTitle = 'Cancel Payment'
      state.confirmDialogText = 'The applied amount will be returned to the short name.'
      state.confirmObject = { item: item, type: ConfirmationType.CANCEL_PAYMENT }
      confirmationDialog.value.open()
    }

    function showConfirmUnlinkAccountModal (item) {
      state.confirmDialogTitle = 'Unlink Account'
      state.confirmDialogText = 'The link with this account will be removed.'
      state.confirmObject = { item: item, type: ConfirmationType.UNLINK_ACCOUNT }
      confirmationDialog.value.open()
    }

    async function cancelPayment (item) {
      state.loading = true
      try {
        await PaymentService.postShortnamePaymentAction(props.shortNameDetails.id,
          item.accountId, ShortNamePaymentActions.CANCEL)
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('An errored occurred cancelling payments pending.', error)
      }
      emit('on-payment-action')
      state.loading = false
    }

    async function unlinkAccount (item) {
      const response = await PaymentService.unlinkShortNameAccount(props.shortNameDetails.id, item.id)
      if (!response) {
        throw new Error('No response from delete short name link')
      }
      await loadShortNameLinks()
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
          await evaluateLinks()
        } else {
          throw new Error('No response from loadShortNameLinks')
        }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Failed to loadShortNameLinks list.', error)
      }
      state.loading = false
    }

    watch(() => props.shortNameDetails, () => {
      getEFTShortNameSummaries()
      loadShortNameLinks()
    })

    return {
      ...toRefs(state),
      state,
      headers,
      isLinked,
      accountDisplayText,
      confirmationDialog,
      openAccountLinkingDialog,
      closeShortNameLinkingDialog,
      dialogConfirm,
      dialogConfirmClose,
      showConfirmCancelPaymentModal,
      showConfirmUnlinkAccountModal,
      onLinkAccount,
      unlinkAccount,
      applyPayment,
      showApplyPayment,
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

.dialog-button-container {
  width: 100%;
  .v-btn {
    width: 106px
  }
}
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
.v-card {
  > div:first-of-type {
    padding: 0!important;
  }
}

::v-deep {
  table {
    box-sizing: content-box;
    thead {
      tr {
        th:first-of-type {
        }
      }
    }
    tbody {
      tr {
        td:first-of-type {
          padding-left: 20px !important;
        }
      }
    }
  }
  .base-table__item-cell {
    padding: 16px 0 16px 0
  }

  // Remove border for rows that are expanded with additional information
  tr:has(+ tr.expanded-item-row) td {
    border-bottom: none !important;
  }
}

.single-action-btn {
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
      color: $gray7;

      .v-icon {
        justify-content: left;
        grid-column: 1;
        padding-right: 4px !important;
        margin-right: 0px !important;
      }
    }

    .alert-item {
      .v-icon{
        color: $app-alert-orange;
      }
    }
  }
}

</style>
