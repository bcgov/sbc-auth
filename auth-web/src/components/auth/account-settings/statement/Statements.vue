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
        v-if="!enableEFTPaymentMethod"
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
      v-if="enableEFTPaymentMethod"
      class="statement-owing"
    >
      <div
        v-if="paymentOwingAmount && paymentDueDate"
        class="total"
      >
        <p class="amount">
          Total Amount Owing: {{ formatAmount(paymentOwingAmount) }}
        </p>
        <p class="date">
          Payment Due Date: {{ formatDate(paymentDueDate) }}
        </p>
      </div>
      <div class="instructions">
        <p><a>How to pay with electronic funds transfer</a></p>
      </div>
    </div>
    <div>
      <v-data-table
        class="statement-list"
        :headers="headerStatements"
        :items="statementsList"
        :custom-sort="customSortActive"
        :no-data-text="$t('noStatementsList')"
        :server-items-length="totalStatementsCount"
        :options.sync="tableDataOptions"
        :loading="isDataLoading"
        loading-text="loading text"
      >
      <!-- <v-data-table
        class="statement-list"
        :headers="headerStatements"
        :items="statementsList"
        :custom-sort="customSortActive"
        :no-data-text="$t('noStatementsList')"
        :server-items-length="totalStatementsCount"
        :options.sync="tableDataOptions"
        :loading="isDataLoading"
        loading-text="loading text"
        :footer-props="{
          itemsPerPageOptions: getPaginationOptions
        }"
      > -->
        <template #loading>
          Loading...
        </template>
        <template #[`item.dateRange`]="{ item }">
          <div class="font-weight-bold">
            {{ formatDateRange(item.fromDate, item.toDate) }}
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
import { ComputedRef, PropType, Ref, computed, defineComponent, onMounted, ref, toRefs, watch } from '@vue/composition-api'
import { useAccountChangeHandler } from '@/composables'
import { Account, LDFlags, Pages } from '@/util/constants'
import { Member, MembershipType, Organization } from '@/models/Organization'
import { StatementFilterParams, StatementListItem } from '@/models/statement'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import CommonUtils from '@/util/common-util'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import StatementsSettings from '@/components/auth/account-settings/statement/StatementsSettings.vue'
import moment from 'moment'
import { useOrgStore } from '@/stores/org'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'

export default defineComponent({
  name: 'StatementsView',
  components: {
    StatementsSettings
  },
  props: {
    orgId: {
      type: String as PropType<string>,
      default: ''
    }
  },
  setup (props, {root}) {
    const orgStore = useOrgStore()
    const currentOrganization: ComputedRef<Organization> = computed(() => orgStore.currentOrganization)
    const currentMembership: ComputedRef<Member> = computed(() => orgStore.currentMembership)
    const { setAccountChangedHandler } = useAccountChangeHandler()
    const getStatement = ref<(statementParams: any) => any>()
    const ITEMS_PER_PAGE = ref<number>(5)
    const PAGINATION_COUNTER_STEP = ref<number>(4)
    const totalStatementsCount = ref<number>(0)
    const tableDataOptions = ref<any>({})
    const isDataLoading = ref<boolean>(false)
    const statementsList = ref<StatementListItem[]>([])
    const isLoading = ref(false)
    const paymentOwingAmount = ref<number>(0)
    const paymentDueDate = ref<Date>(null)
    const statementSettingsModal: Ref<InstanceType<typeof ModalDialog>> = ref(null)

    const getStatementsList = (filterParams: any): any => {
      return computed(() => orgStore.getStatementsList(filterParams))
}

    const headerStatements = ref([
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
        text: 'Downloads',
        align: 'right',
        sortable: false,
        value: 'action'
      }
    ])

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

    const downloadStatement = async (item, type) => {
      isLoading.value = true // to avoid rapid download clicks
      try {
        const downloadType = (type === 'CSV') ? 'text/csv' : 'application/pdf'
        const response = await getStatement({ statementId: item.id, type: downloadType })
        const contentDispArr = response?.headers['content-disposition'].split('=')
        const fileName = (contentDispArr.length && contentDispArr[1]) ? contentDispArr[1] : `bcregistry-statement-${type.toLowerCase()}`
        CommonUtils.fileDownload(response.data, fileName, downloadType)
        isLoading.value = false
      } catch (error) {
        isLoading.value = false
      }
    }

    const enableEFTPaymentMethod = async () => {
      const enableEFTPaymentMethod: string = LaunchDarklyService.getFlag(LDFlags.EnableEFTPaymentMethod) || false
      return enableEFTPaymentMethod
    }

    const customSortActive = async (items, index, isDescending) => {
      const isDesc = isDescending.length > 0 && isDescending[0]
      items.sort((a, b) => {
        return (isDesc) ? (a[index[0]] < b[index[0]] ? -1 : 1) : (b[index[0]] < a[index[0]] ? -1 : 1)
      })
      return items
    }

    const getIndexedTag = async (tag, index) => {
      return `${tag}-${index}`
    }

    const getMomentDateObj = async (dateStr) => {
      return moment(dateStr, 'YYYY-MM-DD')
    }

    const formatDateRange = async (date1, date2) => {
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

    const loadStatementsList = async (pageNumber?: number, itemsPerPage?: number) => {
      isDataLoading.value = true
      const filterParams: StatementFilterParams = {
        pageNumber: pageNumber,
        pageLimit: itemsPerPage
      }
      const resp = await getStatementsList(filterParams)
      statementsList.value = resp?.items || []
      totalStatementsCount.value = resp?.total || 0
      isDataLoading.value = false
    }

    const isStatementsAllowed = async () => {
      return [Account.PREMIUM, Account.STAFF, Account.SBC_STAFF].includes(currentOrganization.value?.orgType as Account) &&
        [MembershipType.Admin, MembershipType.Coordinator].includes(currentMembership.value.membershipTypeCode)
    }

    const initialize = async () => {
      if (!isStatementsAllowed) {
        // if the account switching happening when the user is already in the statements page,
        // redirect to account info if its a basic account
        root.$router.push(`/${Pages.MAIN}/${currentOrganization.value.id}/settings/account-info`)
      } else {
        await loadStatementsList()
      }
    }

    const openSettingsModal = async () => {
      statementSettingsModal.value?.openSettings()
    }

    onMounted(async () => {
      setAccountChangedHandler(initialize)
      initialize()
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
      headerStatements,
      getPaginationOptions,
      customSortActive,
      formatDateRange,
      getIndexedTag,
      openSettingsModal,
      statementsList,
      totalStatementsCount,
      tableDataOptions,
      isDataLoading,
      statementSettingsModal
    }
  }
})
</script>

<style lang="scss" scoped>
.statement-owing {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  .total {
    flex: 0 0 300px;
    .amount {
      font-size: 18px;
      font-weight: 600;
      color: #495057;
      margin: 0;
    }
    .date {
      font-size: 14px;
      font-weight: 400;
      color: #495057
    }
  }
}
.instructions {
  margin-bottom: 30px;
  flex: 1 0 auto;
  p {
    margin: 0;
    text-align: right;
    font-size: 16px;
    a {
      &:hover {
        text-decoration: underline;
      }
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
