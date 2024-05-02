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
    <div
      v-if="enableEFTPaymentMethod && hasEFTPaymentMethod"
      class="statement-owing d-flex flex-wrap flex-row"
    >
      <div
        v-if="paymentOwingAmount && paymentDueDate"
        class="total"
      >
        <p class="amount font-weight-bold">
          Total Amount Owing: {{ formatAmount(paymentOwingAmount) }}
        </p>
        <p class="date font-weight-regular">
          Payment Due Date: {{ formatDate(paymentDueDate) }}
        </p>
      </div>
      <div class="instructions d-flex ma-0 justify-end align-end">
        <p class="text-right ma-0">
          <a @click="getEftInstructions">How to pay with electronic funds transfer</a>
        </p>
      </div>
    </div>
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
import { Account, LDFlags, Pages, PaymentTypes } from '@/util/constants'
import { Member, MembershipType, OrgPaymentDetails, Organization } from '@/models/Organization'
import { PropType, Ref, defineComponent, onMounted, ref, watch } from '@vue/composition-api'
import { StatementFilterParams, StatementListItem } from '@/models/statement'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import CommonUtils from '@/util/common-util'
import DocumentService from '@/services/document.services'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'

import StatementsSettings from '@/components/auth/account-settings/statement/StatementsSettings.vue'
import moment from 'moment'
import { paymentTypeDisplay } from '../../../../resources/display-mappers'
import { useAccountChangeHandler } from '@/composables'
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
    const totalStatementsCount = ref<number>(0)
    const tableDataOptions = ref<any>({})
    const isDataLoading = ref<boolean>(false)
    const statementsList = ref<StatementListItem[]>([])
    const isLoading = ref(false)
    const paymentOwingAmount = ref<number>(0)
    const paymentDueDate = ref<Date>(null)
    const statementSettingsModal: Ref<InstanceType<typeof ModalDialog>> = ref(null)
    const hasEFTPaymentMethod = ref(false)

    const isStatementNew = (item: StatementListItem) => {
      return item.isNew
    }

    const isStatementOverdue = (item: StatementListItem) => {
      return item.isOverdue
    }

    const getEftInstructions = async (): Promise<any> => {
      isLoading.value = true
      try {
        const downloadData = await DocumentService.getEftInstructions()
        CommonUtils.fileDownload(downloadData?.data, `bcrs_eft_instructions.pdf`, downloadData?.headers['content-type'])
      } catch (error) {
        // eslint-disable-next-line no-console
        console.log(error)
      } finally {
        isLoading.value = false
      }
    }

    const getStatementsList = async (filterParams: any): Promise<any> => {
      const data = await orgStore.getStatementsList(filterParams)
      return data
    }

    const getStatementsSummary = async (): Promise<any> => {
      try {
        const data = await orgStore.getStatementsSummary()
        paymentOwingAmount.value = data?.totalDue
        paymentDueDate.value = data?.oldestOverdueDate
        return data
      } catch (error) {
        // eslint-disable-next-line no-console
        console.log(error)
      }
    }

    const downloadStatement = async (item, type) => {
      isLoading.value = true
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
        isLoading.value = false
      }
    }

    const loadStatementsList = async (pageNumber?: number, itemsPerPage?: number) => {
      isDataLoading.value = true
      const filterParams: StatementFilterParams = {
        pageNumber: pageNumber,
        pageLimit: itemsPerPage
      }
      const getStatementsListResponse = await getStatementsList(filterParams)

      if ((pageNumber === 1 || !pageNumber) && getStatementsListResponse?.items?.length > 0) {
        const maxId = Math.max(...getStatementsListResponse.items.map(item => item.id))
        getStatementsListResponse.items.forEach(item => { item.isNew = item.id === maxId })
      }

      statementsList.value = getStatementsListResponse?.items || []
      totalStatementsCount.value = getStatementsListResponse?.total || 0
      isDataLoading.value = false
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
        await loadStatementsList()
        await getStatementsSummary()
      }
    }

    const openSettingsModal = () => {
      statementSettingsModal.value?.openSettings()
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

    const enableEFTPaymentMethod = async () => {
      const enableEFTPaymentMethod: string | boolean = LaunchDarklyService.getFlag(LDFlags.EnableEFTPaymentMethod, false)
      return enableEFTPaymentMethod
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
        hasEFTPaymentMethod.value = paymentMethod
      } catch (error) {
        // eslint-disable-next-line no-console
        console.log(error)
      }
    }

    onMounted(async () => {
      setAccountChangedHandler(initialize)
      initialize()
      getOrgPayments()
    })

    watch(tableDataOptions, (newValue) => {
      const pageNumber = newValue.page || 1
      const itemsPerPage = newValue.itemsPerPage
      loadStatementsList(pageNumber, itemsPerPage)
    }, { immediate: true })

    return {
      formatDate,
      formatAmount,
      isLoading,
      downloadStatement,
      enableEFTPaymentMethod,
      paymentOwingAmount,
      paymentDueDate,
      isStatementNew,
      isStatementOverdue,
      getEftInstructions,
      getPaginationOptions,
      customSortActive,
      formatDateRange,
      frequencyDisplay,
      paymentMethodsDisplay,
      getIndexedTag,
      openSettingsModal,
      statementsList,
      totalStatementsCount,
      tableDataOptions,
      isDataLoading,
      statementSettingsModal,
      hasEFTPaymentMethod
    }
  },
  computed: {
    headerStatements (): any[] {
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

      if (this.hasEFTPaymentMethod && this.enableEFTPaymentMethod()) {
        headers.splice(2, 0, { text: 'Payment Methods', align: 'left', sortable: false, value: 'paymentMethods' })
        headers.splice(3, 0, { text: 'Statement Number', align: 'left', sortable: false, value: 'statementNumber' })
      }

      return headers
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
    flex: 0 0 300px;
    .amount {
      font-size: 18px;
      color: $app-red;
      margin: 0;
    }
    .date {
      font-size: 14px;
      color: $app-red;
      margin: 0;
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
</style>
