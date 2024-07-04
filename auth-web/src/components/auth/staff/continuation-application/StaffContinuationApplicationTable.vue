<template>
  <div id="continuation-application-review-table">
    <v-form class="fas-search continuation-application-search">
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
              :footer-props="{
                itemsPerPageOptions: paginationOptions
              }"
              hide-default-header
              fixed-header
              :loading="isTableLoading"
              :mobile-breakpoint="0"
            >
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
                <div class="py-8 no-data">
                  No data available
                </div>
              </template>

              <!-- Headers (two rows) -->
              <template #header="{}">
                <thead class="v-data-table-header">
                  <!-- First row has titles. -->
                  <tr class="header-row-1">
                    <th
                      v-for="(header, i) in headers"
                      :key="i"
                      class="font-weight-bold"
                    >
                      {{ header.text }}
                    </th>
                  </tr>

                  <!-- Second row has search boxes. Search and filter to be implemented -->
                  <tr class="header-row-2 mt-2 px-2">
                    <th
                      v-for="(header, i) in headers"
                      :key="getIndexedTag('find-header-row2', i)"
                      :scope="getIndexedTag('find-header-col2', i)"
                    >
                      <v-text-field
                        v-if="!['action'].includes(header.value)"
                        :id="header.value"
                        input
                        type="search"
                        autocomplete="off"
                        class="text-input-style"
                        filled
                        :placeholder="header.text"
                        dense
                        hide-details="auto"
                      />
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
                      :data-test="getIndexedTag('view-continuation-button', item.reviewId)"
                      @click="view(item.reviewId)"
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
import { defineComponent, reactive } from '@vue/composition-api'
import BusinessServices from '@/services/business.services'

export default defineComponent({
  name: 'ContinuationReviewTable',
  setup () {
    const state = reactive({
      reviews: [],
      headers: [
        { text: 'Date Submitted', value: 'date' },
        { text: 'NR Number', value: 'nrNumber' },
        { text: 'Identifying Number', value: 'businessIdentifier' },
        { text: 'Completing Party', value: 'completingParty' },
        { text: 'Status', value: 'status' },
        { text: 'Actions', value: 'action' }
      ],
      isTableLoading: false,
      paginationOptions: [5, 10, 15, 20]
    })

    function getButtonLabel (status) {
      const reviewStates = ['Awaiting Review', 'Resubmitted']
      return reviewStates.includes(status) ? 'Review' : 'View'
    }

    function view (reviewId: string) {
      // route to Continuation Authorization Review page
      this.$router.push(`/staff/continuation-review/${reviewId}`)
    }

    function getIndexedTag (tag: string, index: number): string {
      return `${tag}-${index}`
    }

    return {
      ...state,
      getButtonLabel,
      view,
      getIndexedTag
    }
  },
  mounted () {
    this.isTableLoading = true
    BusinessServices.fetchContinuationReviews()
      .then(result => {
        this.reviews = result.data
      })
      .catch(error => {
        console.error('Failed to fetch reviews:', error)
      })
      .finally(() => {
        this.isTableLoading = false
      })
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

.continuation-application-search {
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
