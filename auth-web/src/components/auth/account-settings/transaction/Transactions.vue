<template>
  <v-container class="transaction-container">
    <header v-if="title" class="view-header align-center mb-5 ml-4">
      <h2 class="view-header__title">{{ title }}</h2>
    </header>
    <section v-if="showCredit && credit !== 0">
      <v-divider class="mb-8"></v-divider>
      <h2>Account Credit: <span class="cad-credit ml-4">CAD</span> ${{credit.toFixed(2)}}</h2>
      <p class="credit-details mt-1">You have a credit of ${{credit.toFixed(2)}} on this account.</p>
      <v-divider class="mb-8 mt-8"></v-divider>
    </section>
    <section>
      <v-row justify="end" no-gutters>
        <v-col v-if="showExport">
          <v-btn
            large
            color="primary"
            class="font-weight-bold ml-4"
            :loading="isLoading"
            @click="exportCSV()"
            :disabled="isLoading"
            data-test="btn-export-csv"
          >Export CSV</v-btn>
        </v-col>
        <v-col align-self="end" cols="auto">
          <v-select
            class="column-selections"
            dense
            filled
            hide-details
            item-text="value"
            :items="headerSelections"
            :menu-props="{
              bottom: true,
              minWidth: '200px',
              maxHeight: 'none',
              offsetY: true
            }"
            multiple
            return-object
            style="width: 200px;"
            v-model="headersSelected"
          >
            <template v-slot:selection="{ index }">
              <span v-if="index === 0" class="columns-to-show">Columns to show</span>
            </template>
          </v-select>
        </v-col>
      </v-row>
      <TransactionsDataTable class="mt-4" :extended="extended" :headers="sortedHeaders" />
    </section>
    <!-- export csv error -->
    <ModalDialog
      ref="csvErrorDialog"
      dialog-class="notify-dialog"
      title="Unable to export CSV"
      :text="csvErrorDialogText"
      max-width="640"
    >
      <template v-slot:icon>
        <v-icon large color="primary">mdi-alert-circle-outline</v-icon>
      </template>
      <template v-slot:actions>
        <v-btn large color="primary" @click="csvErrorDialog.close()">OK</v-btn>
      </template>
    </ModalDialog>
  </v-container>
</template>

<script lang="ts">
import { Account, Pages } from '@/util/constants'
import { Member, MembershipType, OrgPaymentDetails, Organization } from '@/models/Organization'
import { Ref, computed, defineComponent, onBeforeUnmount, onMounted, ref, watch } from '@vue/composition-api'
import { useAccountChangeHandler, useTransactions } from '@/composables'
import { BaseTableHeaderI } from '@/components/datatable/interfaces'
import CommonUtils from '@/util/common-util'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { StatusCodes } from 'http-status-codes'
import TransactionsDataTable from './TransactionsDataTable.vue'
import { getTransactionTableHeaders } from '@/resources/table-headers'
import moment from 'moment'
import { useStore } from 'vuex-composition-helpers'

export default defineComponent({
  name: 'Transactions',
  components: { ModalDialog, TransactionsDataTable },
  props: {
    extended: { default: false },
    showCredit: { default: true },
    showExport: { default: true },
    title: { default: '' }
  },
  setup (props, { root }) {
    // store stuff
    const store = useStore()
    const currentOrgPaymentDetails = computed(() => store.state.org.currentOrgPaymentDetails as OrgPaymentDetails)
    const getOrgPayments = (orgId?: number) => store.dispatch('org/getOrgPayments', orgId)
    const currentOrganization = computed(() => store.state.org.currentOrganization as Organization)
    const currentMembership = computed(() => store.state.org.currentMembership as Member)

    const csvErrorDialog: Ref<InstanceType<typeof ModalDialog>> = ref(null)
    const csvErrorTextBasic = 'We were unable to process your CSV export. Please try again later.'
    const csvErrorTextMaxExceeded = 'You have exceeded the maximum of 60,000 records for your CSV export. Please refine your search and try again.'
    const csvErrorDialogText = ref(csvErrorTextBasic)

    const { setAccountChangedHandler, beforeDestroy } = useAccountChangeHandler()
    const { clearAllFilters, getTransactionReport, loadTransactionList, setViewAll } = useTransactions()

    // FUTURE: vue3 we can set this fn explicitly in the resource instead of doing it here
    const headers = getTransactionTableHeaders(props.extended)
    headers.forEach((header) => {
      if (header.hasFilter) {
        header.customFilter.filterApiFn = (val: any) => loadTransactionList(header.col, val || '', props.extended)
      }
    })

    // dynamic header selection stuff
    let preSelectedHeaders = ['createdOn', 'total', 'paymentMethod', 'statusCode', 'actions']
    if (props.extended) preSelectedHeaders = ['accountName', 'appType', 'lineItems', ...preSelectedHeaders]
    else preSelectedHeaders = ['lineItemsAndDetails', ...preSelectedHeaders]

    const headerSelections: BaseTableHeaderI[] = [] // what the user sees in the dropdown
    const headersSelected: Ref<BaseTableHeaderI[]> = ref([]) // headers shown in the table
    headers.forEach((header) => {
      // don't push actions to selection options (want it to be invisible to user)
      if (header.col !== 'actions') headerSelections.push(header)
      if (preSelectedHeaders.includes(header.col)) {
        headersSelected.value.push(header)
      }
    })
    // NB: keeps headers in order after selecting/unselecting columns
    const sortedHeaders: Ref<BaseTableHeaderI[]> = ref([...headersSelected.value])
    watch(() => headersSelected.value, (val: BaseTableHeaderI[]) => {
      // sort headers
      sortedHeaders.value = []
      headers.forEach((header) => {
        if (val.find((selectedHeader) => selectedHeader.col === header.col)) sortedHeaders.value.push(header)
      })
    })

    const credit = ref(0)
    const isLoading = ref(false)

    const isTransactionsAllowed = computed((): boolean => {
      return [Account.PREMIUM, Account.STAFF, Account.SBC_STAFF].includes(currentOrganization.value.orgType as Account) &&
        [MembershipType.Admin, MembershipType.Coordinator].includes(currentMembership.value.membershipTypeCode)
    })

    const getPaymentDetails = async () => {
      const accountId = currentOrgPaymentDetails.value?.accountId
      if (!accountId || Number(accountId) !== currentOrganization.value?.id) {
        const paymentDetails: OrgPaymentDetails = await getOrgPayments(currentOrganization.value?.id)
        credit.value = Number(paymentDetails?.credit || 0)
      } else {
        credit.value = Number(currentOrgPaymentDetails.value?.credit || 0)
      }
    }

    const initUser = () => {
      if (isTransactionsAllowed) getPaymentDetails()
      else {
        // if the account switing happening when the user is already in the transaction page,
        // redirect to account info if its a basic account
        root.$router.push(`/${Pages.MAIN}/currentOrganization.id}/settings/account-info`)
      }
    }

    onMounted(() => {
      setAccountChangedHandler(initUser)
      setViewAll(props.extended)
      clearAllFilters()
      loadTransactionList()
    })
    onBeforeUnmount(() => { beforeDestroy() })

    const exportCSV = async () => {
      isLoading.value = true
      // grab from composable**
      const downloadData = await getTransactionReport()
      if (!downloadData || downloadData.error) {
        if (downloadData?.error?.response?.status === StatusCodes.BAD_REQUEST) {
          csvErrorDialogText.value = csvErrorTextMaxExceeded
        }
        csvErrorDialog.value.open()
      } else {
        CommonUtils.fileDownload(downloadData, `bcregistry-transactions-${moment().format('MM-DD-YYYY')}.csv`, 'text/csv')
      }
      isLoading.value = false
    }

    return {
      csvErrorDialog,
      csvErrorDialogText,
      headers,
      headerSelections,
      headersSelected,
      sortedHeaders,
      credit,
      isLoading,
      exportCSV
    }
  }
})
</script>

<style lang="scss" scoped>
@import "$assets/scss/theme.scss";
  .columns-to-show {
    color: $gray7;
    font-size: 0.825rem;
  }

  .view-header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }

  .transaction-container {
    overflow: hidden;
  }

  .folio-number-field {
    border-top-right-radius: 0px;
    border-bottom-right-radius: 0px;
    max-width: 180px;
  }

  .folio-number-apply-btn {
    border-top-left-radius: 0px;
    border-bottom-left-radius: 0px;
  }

  .date-filter-container {
    .date-range-list {
      border-right: 1px solid #999;
      padding-right: 0;
    }
  }

  .date-range-options {
    width: 15rem;
    border-radius: 0 !important;
    border-right: 1px solid var(--v-grey-lighten1);
  }

  .date-range-label {
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--v-grey-lighten1);
  }

  .v-picker.v-card {
    box-shadow: none !important;
  }

  .filter-results {
    opacity: 0;
    overflow: hidden;
    max-height: 0;
    transition: all ease-out 0.25s;
  }

  .filter-results.active {
    opacity: 1;
    max-height: 4rem;
  }

  .filter-results-label {
    font-weight: 700;
  }

  .v-chip {
    height: 36px;
  }

  ::v-deep {
    .v-text-field--outlined.v-input--dense .v-label {
      top: 14px !important;
    }

    .v-progress-linear {
      margin-top: -2px !important
    }
  }
  .cad-credit {
    font-size: 14px;
    color: $gray6;
  }
  .credit-details {
     color: $gray7;
  }
</style>
