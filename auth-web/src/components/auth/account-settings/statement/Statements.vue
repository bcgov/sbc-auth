<template>
  <v-container>
    <v-fade-transition>
      <div
        v-if="isLoading"
        class="loading-container"
      >
        <v-progress-circular
          size="50"
          width="5"
          color="primary"
          :indeterminate="isLoading"
        />
      </div>
    </v-fade-transition>
    <header class="view-header">
      <h2 class="view-header__title">
        Statements
      </h2>
      <v-btn
        large
        depressed
        aria-label="Statement Settings"
        title="Open Statement Settings"
        @click.stop="openSettingsModal"
      >
        <v-icon
          small
          class="mr-2 ml-n1"
        >
          mdi-settings
        </v-icon>
        Settings
      </v-btn>
    </header>
    <template v-if="enableEFTPaymentMethod && hasEFTPaymentMethod && paymentOwingAmount >= 0">
      <div
        class="statement-owing d-flex flex-wrap flex-row  mb-2"
      >
        <div
          class="total"
        >
          <p
            class="amount font-weight-bold"
            :class="{ 'owing' : paymentDueDate}"
          >
            Total Amount Owing: {{ formatAmount(paymentOwingAmount) }}
          </p>
          <p class="font-weight-regular">
            <span
              v-if="paymentDueDate"
              class="due-date"
            >Payment Due Date: {{ formatDate(paymentDueDate) }}</span>
            <span
              v-else
              class="non-due-date"
            >Next statement will be available on {{ nextStatementDate }}</span>
          </p>
        </div>
        <div class="instructions d-flex ma-0 justify-end align-end">
          <p class="text-right ma-0">
            <a @click="downloadEFTInstructions">How to pay with electronic funds transfer</a>
          </p>
        </div>
      </div>
      <div
        v-if="shortNameLinksCount > 1 && isEftUnderPayment"
        class="flex-row mt-4"
      >
        <v-alert
          class="mt-3 mb-0 alert-item account-alert-inner"
          :icon="false"
          prominent
          outlined
          type="warning"
        >
          <div class="account-alert-inner mb-0">
            <v-icon
              medium
            >
              mdi-alert
            </v-icon>
            <p class="account-alert__info mb-0 pl-3">
              <strong>Caution:</strong> Recent partial payments are not reflected in amount owing. Payment will not be
              applied to the amount owing until full amount has been received for <strong>all accounts</strong> that are
              linked to your short name.
            </p>
          </div>
        </v-alert>
      </div>
    </template>
    <div>
      <v-data-table
        class="statement-list"
        :headers="headerStatements"
        :items="statementsList"
        :no-data-text="$t('noStatementsList')"
        :server-items-length="totalStatementsCount"
        :options.sync="tableDataOptions"
        :custom-sort="customSortActive"
        :loading="isDataLoading"
        loading-text="loading text"
        :footer-props="{ itemsPerPageOptions: [5, 10, 15, 20] }"
      >
        <template #loading>
          Loading...
        </template>
        <template #[`item.dateRange`]="{ item }">
          <div class="font-weight-bold">
            <span>{{ formatDateRange(item.fromDate, item.toDate) }}</span>
            <span
              v-if="isStatementNew(item)"
              class="label ml-2 px-2 d-inline-block"
            >NEW</span>
            <span
              v-if="isStatementOverdue(item)"
              class="label overdue ml-2 px-2 d-inline-block"
            >OVERDUE</span>
          </div>
        </template>
        <template
          v-if="enableEFTPaymentMethod && hasEFTPaymentMethod"
          #[`item.frequency`]="{ item }"
        >
          <div>
            <span>{{ frequencyDisplay(item) }}</span>
          </div>
        </template>
        <template
          v-if="enableEFTPaymentMethod && hasEFTPaymentMethod"
          #[`item.paymentMethods`]="{ item }"
        >
          <div>
            <span>{{ paymentMethodsDisplay(item.paymentMethods) }}</span>
          </div>
        </template>
        <template
          #[`item.statementNumber`]="{ item }"
        >
          <div>
            <span>{{ item.id }}</span>
          </div>
        </template>
        <template #[`item.action`]="{ item }">
          <div>
            <v-btn
              text
              color="primary"
              class="mr-1"
              aria-label="Download CSV"
              title="Download statement as a CSV file"
              :data-test="getIndexedTag('csv-button', item.id)"
              @click="downloadStatement(item, 'CSV')"
            >
              <v-icon class="ml-n2">
                mdi-file-table-outline
              </v-icon>
              <span class="ml-n1 font-weight-bold">CSV</span>
            </v-btn>
            <v-btn
              text
              color="primary"
              aria-label="Download PDF"
              title="Download statement as a PDF file"
              :data-test="getIndexedTag('pdf-button', item.id)"
              @click="downloadStatement(item, 'PDF')"
            >
              <v-icon class="ml-n2">
                mdi-file-pdf-outline
              </v-icon>
              <span class="ml-n1 font-weight-bold">PDF</span>
            </v-btn>
          </div>
        </template>
      </v-data-table>
    </div>
    <StatementsSettings
      ref="statementSettingsModal"
    />
  </v-container>
</template>

<script lang="ts">
import { Account, LDFlags, Pages, PaymentTypes, SessionStorageKeys } from '@/util/constants'
import { Member, MembershipType, OrgPaymentDetails, Organization } from '@/models/Organization'
import { PropType, computed, defineComponent, onMounted, reactive, toRefs, watch } from '@vue/composition-api'
import { StatementFilterParams, StatementListItem } from '@/models/statement'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import CommonUtils from '@/util/common-util'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'

import StatementsSettings from '@/components/auth/account-settings/statement/StatementsSettings.vue'
import moment from 'moment'
import { paymentTypeDisplay } from '../../../../resources/display-mappers'
import { useAccountChangeHandler } from '@/composables'
import { useDownloader } from '@/composables/downloader'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  name: 'StatementsView',
  components: { StatementsSettings },
  mixins: [AccountChangeMixin],
  props: {
    orgId: {
      type: String as PropType<string>,
      default: ''
    }
  },
  setup (props, { root }) {
    const ITEMS_PER_PAGE = 5
    const PAGINATION_COUNTER_STEP = 4
    const orgStore = useOrgStore()
    const currentOrganization: Organization = orgStore.currentOrganization
    const currentMembership: Member = orgStore.currentMembership
    const getStatement: any = orgStore.getStatement
    const { setAccountChangedHandler } = useAccountChangeHandler()

    const enableEFTPaymentMethod = async () => {
      const enableEFTPaymentMethod: string | boolean = LaunchDarklyService.getFlag(LDFlags.EnableEFTPaymentMethod, false)
      return enableEFTPaymentMethod
    }

    const state = reactive({
      totalStatementsCount: 0,
      tableDataOptions: {},
      isDataLoading: false,
      statementsList: [],
      isLoading: false,
      paymentOwingAmount: -1,
      paymentDueDate: null,
      shortNameLinksCount: 0,
      isEftUnderPayment: false,
      statementSettingsModal: null,
      hasEFTPaymentMethod: false,
      headerStatements: computed(() => {
        const headers = [
          {
            text: 'Date',
            align: 'left',
            sortable: false,
            value: 'dateRange'
          },
          {
            text: 'Frequency',
            align: 'left',
            sortable: false,
            value: 'frequency'
          },
          {
            text: 'Statement Number',
            align: 'left',
            sortable: false,
            value: 'statementNumber'
          },
          {
            text: 'Downloads',
            align: 'right',
            sortable: false,
            value: 'action'
          }
        ]
        if (state.hasEFTPaymentMethod && enableEFTPaymentMethod()) {
          headers.splice(2, 0, { text: 'Payment Methods', align: 'left', sortable: false, value: 'paymentMethods' })
        }
        return headers
      }),
      nextStatementDate: computed<string>(() => {
        return moment().add(1, 'M').startOf('month').format('MMMM D, YYYY')
      })
    })

    const { downloadEFTInstructions } = useDownloader(orgStore, state)

    const isStatementNew = (item: StatementListItem) => {
      let isNew = item.isNew
      const statementsDownloaded = JSON.parse(sessionStorage.getItem(SessionStorageKeys.StatementsDownloaded)) || []
      if (statementsDownloaded?.includes(item.id)) {
        isNew = false
      }
      return isNew
    }

    const isStatementOverdue = (item: StatementListItem) => {
      return item.isOverdue
    }

    const getStatementsList = async (filterParams: any): Promise<any> => {
      const data = await orgStore.getStatementsList(filterParams)
      return data
    }

    const getStatementsSummary = async (): Promise<any> => {
      try {
        const data = await orgStore.getStatementsSummary()
        state.paymentOwingAmount = data?.totalDue
        state.paymentDueDate = data?.oldestDueDate
        state.shortNameLinksCount = data?.shortNameLinksCount
        state.isEftUnderPayment = data?.isEftUnderPayment
        return data
      } catch (error) {
        // eslint-disable-next-line no-console
        console.log(error)
      }
    }

    const downloadStatement = async (item, type) => {
      state.isLoading = true
      try {
        const downloadType = (type === 'CSV') ? 'text/csv' : 'application/pdf'
        const response = await getStatement({ statementId: item.id, type: downloadType })
        const contentDispArr = response?.headers['content-disposition'].split('=')
        const fileName = (contentDispArr.length && contentDispArr[1]) ? contentDispArr[1] : `bcregistry-statement-${type.toLowerCase()}`
        CommonUtils.fileDownload(response.data, fileName, downloadType)
      } catch (error) {
        // eslint-disable-next-line no-console
        console.log(error)
      } finally {
        const statementsDownloaded = JSON.parse(sessionStorage.getItem(SessionStorageKeys.StatementsDownloaded)) || []
        statementsDownloaded.push(item.id)
        sessionStorage.setItem(SessionStorageKeys.StatementsDownloaded, JSON.stringify(statementsDownloaded))
        state.isLoading = false
      }
    }

    const loadStatementsList = async (pageNumber?: number, itemsPerPage?: number) => {
      state.isDataLoading = true
      const filterParams: StatementFilterParams = {
        pageNumber: pageNumber,
        pageLimit: itemsPerPage
      }
      const getStatementsListResponse = await getStatementsList(filterParams)

      if ((pageNumber === 1 || !pageNumber) && getStatementsListResponse?.items?.length > 0) {
        getStatementsListResponse.items[0].isNew = true
      }

      state.statementsList = getStatementsListResponse?.items || []
      state.totalStatementsCount = getStatementsListResponse?.total || 0
      state.isDataLoading = false
    }

    const isStatementsAllowed = async () => {
      return (orgStore.isStaffOrSbcStaff || currentOrganization?.orgType === Account.PREMIUM) &&
        [MembershipType.Admin, MembershipType.Coordinator].includes(currentMembership.membershipTypeCode)
    }

    const initialize = async () => {
      if (!isStatementsAllowed) {
        // if the account switching happening when the user is already in the statements page,
        // redirect to account info if its a basic account
        root.$router.push(`/${Pages.MAIN}/${currentOrganization.id}/settings/account-info`)
      } else {
        const promises = [loadStatementsList()];
        if (state.hasEFTPaymentMethod) {
            promises.push(getStatementsSummary());
        }
        await Promise.all(promises)
      }
    }

    const openSettingsModal = () => {
      state.statementSettingsModal.openSettings()
    }

    const customSortActive = (items, index, isDescending) => {
      const isDesc = isDescending.length > 0 && isDescending[0]
      items.sort((a, b) => {
        return (isDesc) ? (a[index[0]] < b[index[0]] ? -1 : 1) : (b[index[0]] < a[index[0]] ? -1 : 1)
      })
      return items
    }

    const formatDate = (val: string) => {
      const date = moment.utc(val).toDate()
      return CommonUtils.formatDisplayDate(date, 'MMMM DD, YYYY')
    }

    const formatAmount = (amount: number) => {
      return CommonUtils.formatAmount(amount)
    }

    const getPaginationOptions = () => {
      return [...Array(PAGINATION_COUNTER_STEP)].map((value, index) => ITEMS_PER_PAGE * (index + 1))
    }

    const getIndexedTag = (tag, index) => {
      return `${tag}-${index}`
    }

    const getMomentDateObj = (dateStr) => {
      return moment(dateStr, 'YYYY-MM-DD')
    }

    const frequencyDisplay = (item) => {
      const paymentMethods = item.paymentMethods || []
      if (paymentMethods.length > 1) {
        return 'Payment Method Changed'
      }
      return item.frequency
    }

    const paymentMethodsDisplay = (paymentMethods: string[] = []) => {
      return paymentMethods.map(method => paymentTypeDisplay[method]).join(', ')
    }

    const formatDateRange = (date1, date2) => {
      let dateObj1 = getMomentDateObj(date1)
      let dateObj2 = getMomentDateObj(date2)
      let year = (dateObj1.year() === dateObj2.year()) ? dateObj1.year() : ''
      let month = (dateObj1.month() === dateObj2.month()) ? dateObj1.format('MMMM') : ''
      if (date1 === date2) {
        return dateObj1.format('MMMM DD, YYYY')
      } else if (year && !month) {
        return `${dateObj1.format('MMMM DD')} - ${dateObj2.format('MMMM DD')}, ${year}`
      } else if (year && month) {
        return `${month} ${dateObj1.date()} - ${dateObj2.date()}, ${year}`
      } else {
        return `${dateObj1.format('MMMM DD, YYYY')} - ${dateObj2.format('MMMM DD, YYYY')}`
      }
    }

    const getOrgPayments = async () => {
      try {
        const orgPayments: OrgPaymentDetails = await orgStore.getOrgPayments()
        const paymentMethod = orgPayments.paymentMethod === PaymentTypes.EFT
        state.hasEFTPaymentMethod = paymentMethod
      } catch (error) {
        // eslint-disable-next-line no-console
        console.log(error)
      }
    }

    onMounted(async () => {
      setAccountChangedHandler(initialize)
      await getOrgPayments()
      await initialize()
    })

    watch(() => state.tableDataOptions, (newValue: any) => {
      const pageNumber = newValue.page || 1
      const itemsPerPage = newValue.itemsPerPage
      loadStatementsList(pageNumber, itemsPerPage)
    }, { immediate: true })

    return {
      ...toRefs(state),
      formatDate,
      formatAmount,
      downloadStatement,
      downloadEFTInstructions,
      enableEFTPaymentMethod,
      isStatementNew,
      isStatementOverdue,
      getPaginationOptions,
      customSortActive,
      formatDateRange,
      frequencyDisplay,
      paymentMethodsDisplay,
      getIndexedTag,
      openSettingsModal
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.label {
  background: $app-blue;
  color: white;
  border-radius: 4px;
  font-size: 10px;
  &.overdue {
    background: $app-red;
  }
}
.statement-owing {
  .total {
    flex: 0 0 400px;
    .amount {
      font-size: 18px;
      color: $gray7;
      margin: 0;
    }
    .owing {
      color: $app-red;
    }
    .due-date {
      font-size: 14px;
      color: $app-red;
      margin: 0;
    }
    .non-due-date {
      font-size: 14px;
      color: $gray7;
      margin: 0;
    }
    &.owing {
      .amount, .date {
        color: $app-red;
      }
    }
  }
}
.instructions {
  margin-bottom: 30px;
  flex: 1 0 auto;
  p {
    font-size: 16px;
    a {
      color: $app-blue;
      text-decoration: underline;
    }
  }
}
.view-header {
  margin-bottom: 20px;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.statement-list {
  .v-data-table-header {
    margin-bottom: -2px;
  }
}

.loading-container {
  background: rgba(255,255,255, 0.8);
}

.account-alert-inner {
  .v-icon {
    color: $app-red;
  }
  background-color: $app-background-error !important;
  border-color: $app-red !important;
  border-radius: 0;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
}
.account-alert__info {
  flex: 1 1 auto;
  color: $gray7;
  font-size: 12px;
}
</style>
