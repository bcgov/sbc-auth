<template>
  <div id="continuation-application-review-table">
    <v-form class="fas-search continuation-review-search">
      <v-row
        dense
        class="row-margin"
      >
        <v-col
          sm="12"
          cols="6"
        >
          <transition name="slide-fade">
            <v-data-table
              :headers="headers"
              :items="reviews"
              :server-items-length="totalItemsCount"
              :options.sync="tableDataOptions"
              :disable-sort="true"
              :footer-props="{
                itemsPerPageOptions: paginationOptions
              }"
              hide-default-header
              fixed-header
              :loading="isTableLoading"
              :mobile-breakpoint="0"
              @update:options="updateItemsPerPage"
            >
              <!-- Displaying Status -->
              <template #[`item.status`]="{ item }">
                <div>{{ displayStatus(item.status) }}</div>
              </template>

              <!-- Displaying Formatted Date -->
              <template #[`item.submissionDate`]="{ item }">
                <div>{{ formatDate(item.submissionDate) }}</div>
              </template>

              <!-- Loading -->
              <template #loading>
                <div
                  class="py-8 loading-datatable"
                >
                  Loading items...
                </div>
              </template>

              <!-- No data -->
              <template #no-data>
                <div
                  v-sanitize="noDataMessage"
                  class="py-8 no-data"
                />
              </template>

              <!-- Headers (two rows) -->
              <template #header="{}">
                <thead class="v-data-table-header">
                  <!-- First row has titles. -->
                  <tr class="header-row-1">
                    <th
                      v-for="(header, i) in headers"
                      :key="getIndexedTag('find-header-row', i)"
                      :scope="getIndexedTag('find-header-col', i)"
                      class="font-weight-bold"
                    >
                      {{ header.text }}
                    </th>
                  </tr>

                  <!-- Second row has search boxes. -->
                  <tr class="header-row-2 mt-2 px-2">
                    <th
                      v-for="(header, i) in headers"
                      :key="getIndexedTag('find-header-row2', i)"
                      :scope="getIndexedTag('find-header-col2', i)"
                    >
                      <v-text-field
                        v-if="!['action','status'].includes(header.value)"
                        :id="header.value"
                        v-model.trim="reviewParams[header.value]"
                        input
                        type="search"
                        autocomplete="off"
                        class="text-input-style"
                        filled
                        :placeholder="header.text"
                        dense
                        hide-details="auto"
                      />

                      <div
                        v-else-if="['status'].includes(header.value)"
                        class="mt-0"
                      >
                        <v-select
                          v-model="reviewParams[header.value]"
                          :items="statusTypes"
                          filled
                          item-text="text"
                          item-value="value"
                          data-test="select-status"
                          v-bind="$attrs"
                          hide-details="auto"
                          v-on="$listeners"
                        />
                      </div>

                      <v-btn
                        v-else-if="searchParamsExist && header.value === 'action'"
                        outlined
                        color="primary"
                        class="action-btn clear-filter-button"
                        @click="clearSearchParams()"
                      >
                        <span class="clear-filter cursor-pointer">
                          Clear Filters
                          <v-icon
                            small
                            color="primary"
                          >mdi-close</v-icon>
                        </span>
                      </v-btn>
                    </th>
                  </tr>
                </thead>
              </template>

              <!-- Item Actions -->
              <template #[`item.action`]="{ item }">
                <div class="actions text-right">
                  <span class="open-action">
                    <v-btn
                      color="primary"
                      :class="['open-action-btn', getButtonLabel(item.status).toLowerCase()]"
                      :data-test="getIndexedTag('view-continuation-button', item.id)"
                      @click="view(item.id)"
                    >
                      {{ getButtonLabel(item.status) }}
                    </v-btn>
                  </span>
                </div>
              </template>
            </v-data-table>
          </transition>
        </v-col>
      </v-row>
    </v-form>
  </div>
</template>

<script lang="ts">
import { ContinuationReviewIF, ReviewFilterParams } from '@/models/continuation-review'
import {
  DEFAULT_DATA_OPTIONS,
  cachePageInfo,
  getAndPruneCachedPageInfo,
  getPaginationOptions,
  hasCachedPageInfo
} from '@/components/datatable/resources'
import { PropType, computed, defineComponent, reactive, ref, toRefs, watch } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { DataOptions } from 'vuetify'
import { SessionStorageKeys } from '@/util/constants'
import debounce from '@/util/debounce'
import moment from 'moment'
import { useI18n } from 'vue-i18n-composable'
import { useStaffStore } from '@/stores/staff'

export default defineComponent({
  name: 'ContinuationApplicationTable',
  props: {
    reviewSessionStorageKey: {
      type: String as PropType<SessionStorageKeys>,
      default: SessionStorageKeys.ReviewSearchFilter
    },
    reviewPaginationNumberOfItemsKey: {
      type: String as PropType<SessionStorageKeys>,
      default: SessionStorageKeys.ReviewPaginationNumberOfItems
    },
    reviewPaginationOptionsKey: {
      type: String as PropType<SessionStorageKeys>,
      default: SessionStorageKeys.ReviewPaginationOptions
    }
  },
  setup (props) {
    const { t } = useI18n()
    const staffStore = useStaffStore()

    const state = reactive({
      reviews: [] as Array<ContinuationReviewIF>,
      headers: [
        { text: 'Date Submitted', value: 'submissionDate' },
        { text: 'NR Number', value: 'nrNumber' },
        { text: 'Identifying Number', value: 'identifier' },
        { text: 'Completing Party', value: 'completingParty' },
        { text: 'Status', value: 'status' },
        { text: 'Actions', value: 'action' }
      ],
      statusTypes: ref<{ text: string; value: string }[]>([
        { text: 'Awaiting Review', value: 'AWAITING_REVIEW' },
        { text: 'Change Requested', value: 'CHANGE_REQUESTED' },
        { text: 'Resubmitted', value: 'RESUBMITTED' },
        { text: 'Rejected', value: 'REJECTED' },
        { text: 'Accepted', value: 'ACCEPTED' },
        { text: 'Abandoned', value: 'ABANDONED' }
      ]),
      formatDate: CommonUtils.formatDisplayDate,
      totalItemsCount: 0,
      tableDataOptions: {} as Partial<DataOptions>,
      isTableLoading: false,
      searchParamsExist: false,
      dropdown: [] as Array<boolean>,
      reviewParams: {
        submissionDate: '',
        nrNumber: '',
        identifier: '',
        completingParty: '',
        status: ''
      } as ReviewFilterParams
    })

    const paginationOptions = computed(() => getPaginationOptions())

    const debouncedOrgSearch = debounce(async function (page = 1, pageLimit = state.tableDataOptions.itemsPerPage) {
      try {
        state.isTableLoading = true
        const completeSearchParams: ReviewFilterParams = {
          ...state.reviewParams,
          page: page,
          limit: pageLimit
        }
        console.log(completeSearchParams)
        const searchReviewResp = await staffStore.searchReviews(completeSearchParams)
        state.reviews = searchReviewResp.reviews
        state.totalItemsCount = searchReviewResp?.total || 0
      } catch (error) {
        console.error(error)
      } finally {
        state.isTableLoading = false
      }
    })

    function mounted () {
      state.tableDataOptions = DEFAULT_DATA_OPTIONS
      const reviewSearchFilter = ConfigHelper.getFromSession(props.reviewSessionStorageKey) || ''
      try {
        state.reviewParams = JSON.parse(reviewSearchFilter)
      } catch {
        // Do nothing, we have defaults for review searchParams.
      }
      const hasInfo = hasCachedPageInfo(props.reviewPaginationOptionsKey)
      if (hasInfo) {
        state.tableDataOptions = getAndPruneCachedPageInfo(props.reviewPaginationOptionsKey)
      }
    }

    watch(() => state.reviewParams, function (value) {
      state.searchParamsExist = doSearchParametersExist(value)
      state.tableDataOptions = { ...getAndPruneCachedPageInfo(props.reviewPaginationOptionsKey), page: 1 }
      setSearchFilterToStorage(JSON.stringify(value))
      debouncedOrgSearch()
    }, { deep: true })

    watch(() => state.tableDataOptions, function (val) {
      debouncedOrgSearch(val?.page, val?.itemsPerPage)
    }, { deep: true })

    function getButtonLabel (status: string) {
      const reviewStates = ['AWAITING_REVIEW', 'RESUBMITTED']
      return reviewStates.includes(status) ? 'Review' : 'View'
    }
    async function view (reviewId: string) {
      this.$router.push(`/staff/continuation-review/${reviewId}`)
    }

    function clearSearchParams () {
      state.reviewParams = {
        submissionDate: '',
        nrNumber: '',
        identifier: '',
        completingParty: '',
        status: ''
      }
    }

    function getIndexedTag (tag: string, index: number): string {
      return `${tag}-${index}`
    }

    function updateItemsPerPage (options: DataOptions): void {
      cachePageInfo(options, props.reviewPaginationOptionsKey)
    }

    const noDataMessage = computed(() => {
      return t(
        state.searchParamsExist
          ? 'searchReviewsNoResult'
          : 'searchReviewStartMessage'
      )
    })

    function setSearchFilterToStorage (val: string): void {
      ConfigHelper.addToSession(props.reviewSessionStorageKey, val)
    }

    function doSearchParametersExist (params: ReviewFilterParams): boolean {
      return params.submissionDate.length > 0 ||
                params.nrNumber.length > 0 ||
                params.identifier.length > 0 ||
                params.completingParty.length > 0 ||
                params.status.length > 0
    }

    // Method to display the status
    function displayStatus (status: string): string {
      return status
        .toLowerCase()
        .replace(/_/g, ' ')
        .replace(/(^\w{1})|(\s+\w{1})/g, letter => letter.toUpperCase())
    }
    // Method to format dates
    const formatDate = (dateString) => {
      return moment(dateString).format('MMMM D, YYYY') // Format like "May 5, 2024"
    }

    mounted()

    return {
      ...toRefs(state),
      debouncedOrgSearch,
      view,
      clearSearchParams,
      displayStatus,
      formatDate,
      getIndexedTag,
      getButtonLabel,
      noDataMessage,
      setSearchFilterToStorage,
      doSearchParametersExist,
      paginationOptions,
      updateItemsPerPage
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
// Note this uses .fas-search
@import '~/fas-ui/src/assets/scss/search.scss';

// Vuetify Override
.theme--light.v-list-item .v-list-item__action-text, .theme--light.v-list-item .v-list-item__subtitle {
  color: $app-blue;
  .v-icon.v-icon {
    color: $app-blue;
  }
}

// Class binding a vuetify override.
// To handle the sticky elements overlap in the custom scrolling data table.
.header-high-layer {
  ::v-deep {
    th {
      z-index: 2 !important;
    }
  }
}

::v-deep .theme--light.v-data-table .v-data-table__empty-wrapper {
  color: $gray7;
  &:hover {
    background-color: transparent;
  }
}

.business-dashboard-icon {
  opacity: 1;
  width: 14px;
  height: 14px;
  transform: rotate(0deg);
  display: inline-flex;
}

.continuation-review-search {
  table > thead > tr > th {
    width: 210px !important;
    min-width: 210px !important;
  }

  .open-action-btn,
  .more-actions-btn {
    box-shadow: 0 1px 1px 0px rgb(0 0 0 / 20%), 0 2px 2px 0 rgb(0 0 0 / 14%), 0 1px 5px 0 rgb(0 0 0 / 12%);
    -webkit-box-shadow: 0 1px 1px 0px rgb(0 0 0 / 20%), 0 2px 2px 0 rgb(0 0 0 / 14%), 0 1px 5px 0 rgb(0 0 0 / 12%);
  }

  .open-action-btn {
    &.active {
      border-top-right-radius: 0;
      border-bottom-right-radius: 0;
    }
  }

  .open-action-btn.view {
  min-width: 4.9rem !important;
  }

  .open-action-btn.review {
  min-width: 6rem !important;
  }

  .more-actions-btn {
    padding-left: 0px;
    padding-right: 0px;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    max-width: 30px !important;
    min-width: 30px !important;
    margin-left: 0.05rem;
  }

  // Inline for Clear Filters
  .clear-filter-button {
    padding: 7px !important;
  }

  .clear-filter {
    line-height: 1.5;
  }

  // As requested by Tracey.
  ::v-deep input, ::v-deep .v-select__selection {
    color:#212529 !important;
  }

  ::v-deep ::placeholder{
    color:#495057 !important;
  }

  .v-data-table th {
    font-size: 0.75rem;
  }

  ::v-deep .v-data-footer {
    min-width: 100%;
  }

  .no-data, .loading-datatable {
    border: 0px;
    position: sticky;
    width: 1230px;
    left: 0;
    flex-grow: 0;
    flex-shrink: 0;
  }

  ::v-deep .v-data-table__wrapper::-webkit-scrollbar {
    width: .625rem;
    height: 0.50rem;
    overflow-x: hidden;
  }

  ::v-deep .v-data-table__wrapper::-webkit-scrollbar-track {
    overflow: auto;
  }

  ::v-deep .v-data-table__wrapper::-webkit-scrollbar-thumb {
    border-radius: 5px;
    background-color: lightgray;
  }

  table > thead > tr > th:last-child {
    width: 130px !important;
    min-width: 130px !important;
  }

  // The TD cells don't seem to be scoped properly.
  // Thus the usage of v-deep.
  ::v-deep tr:hover td:last-child {
    background-color: inherit !important;
  }

  table > thead > tr > th:last-child,
  ::v-deep table > tbody > tr > td:last-child:not([colspan]) {
    position: sticky !important;
    position: -webkit-sticky !important;
    right: 0;
    z-index: 1;
    background: white;
    text-align: right !important;
  }

 ::v-deep table > tbody > tr > td {
    border: 0px;
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }

  ::v-deep table > tbody > tr > td:last-child:not([colspan]) {
    padding-left: 3px !important;
    padding-right: 3px !important;
  }

}
</style>
