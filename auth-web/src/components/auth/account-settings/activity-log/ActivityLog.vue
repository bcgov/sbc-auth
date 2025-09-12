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
    <header class="view-header mb-6">
      <h2 class="view-header__title">
        Activity Log
      </h2>
    </header>
    <div>
      <v-data-table
        class="activity-list"
        :headers="activityHeader"
        :items="activityList"
        :no-data-text="$t('noActivityLogList')"
        :server-items-length="totalActivityCount"
        :options.sync="tableDataOptions"
        :loading="isDataLoading"
        loading-text="loading text"
        :footer-props="{
          itemsPerPageOptions: getPaginationOptions
        }"
      >
        <template #loading>
          Loading...
        </template>
        <template #[`item.created`]="{ item }">
          <div class="font-weight-bold">
            {{ formatDate(moment.utc(item.created).toDate(), 'MMMM DD, YYYY h:mm A') }}
          </div>
        </template>
      </v-data-table>
    </div>
  </v-container>
</template>

<script lang="ts">
import { ActivityLog, ActivityLogFilterParams } from '@/models/activityLog'
import { PropType, computed, defineComponent, onBeforeUnmount, onMounted, reactive, toRefs, watch } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import moment from 'moment'
import { useActivityStore } from '@/stores/activityLog'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  name: 'ActivityLogs',
  props: {
    orgId: {
      type: Number as PropType<number>,
      default: 0
    }
  },
  setup () {
    const activityStore = useActivityStore()
    const orgStore = useOrgStore()

    const ITEMS_PER_PAGE = 5
    const PAGINATION_COUNTER_STEP = 4

    const state = reactive({
      totalActivityCount: 0,
      tableDataOptions: {},
      isDataLoading: false,
      activityList: [] as ActivityLog[],
      isLoading: false,
      activityHeader: [
        {
          text: 'Date (Pacific Time)',
          align: 'left',
          sortable: false,
          value: 'created',
          class: 'bold-header'
        },
        {
          text: 'Initiated by',
          align: 'left',
          sortable: false,
          value: 'actor',
          class: 'bold-header'
        },
        {
          text: 'Subject',
          align: 'left',
          sortable: false,
          value: 'action',
          class: 'bold-header'
        }
      ]
    })

    const currentOrganization = computed(() => orgStore.currentOrganization)
    const currentMembership = computed(() => orgStore.currentMembership)
    const currentOrgActivity = computed(() => activityStore.currentOrgActivity)

    const getPaginationOptions = computed(() => {
      return [...Array(PAGINATION_COUNTER_STEP)].map((value, index) => ITEMS_PER_PAGE * (index + 1))
    })

    const loadActivityList = async (pageNumber?: number, itemsPerPage?: number) => {
      state.isDataLoading = true
      const filterParams: ActivityLogFilterParams = {
        pageNumber: pageNumber,
        pageLimit: itemsPerPage,
        orgId: currentOrganization.value.id
      }
      try {
        const resp: any = await activityStore.getActivityLog(filterParams)
        state.activityList = resp?.activityLogs || []
        state.totalActivityCount = resp?.total || 0
        state.isDataLoading = false
      } catch {
        state.activityList = []
        state.totalActivityCount = 0
        state.isDataLoading = false
      }
    }

    const initialize = async () => {
      await loadActivityList()
    }

    let unregisterHandler: (() => void) | null = null

    const setAccountChangedHandler = (handler: () => any) => {
      unregisterHandler = orgStore.$onAction(({ name, after }) => {
        after(() => {
          if (['syncOrganization', 'setCurrentOrganization'].includes(name)) {
            handler()
          }
        })
      })
    }

    watch(() => state.tableDataOptions, async (val: any) => {
      const pageNumber = val?.page || 1
      const itemsPerPage = val?.itemsPerPage
      await loadActivityList(pageNumber, itemsPerPage)
    }, { deep: true })

    onMounted(async () => {
      setAccountChangedHandler(initialize)
      await initialize()
    })

    onBeforeUnmount(() => {
      if (unregisterHandler) {
        unregisterHandler()
      }
    })

    return {
      ...toRefs(state),
      currentOrganization,
      currentMembership,
      currentOrgActivity,
      getPaginationOptions,
      formatDate: CommonUtils.formatDisplayDate,
      loadActivityList,
      initialize,
      moment
    }
  }
})
</script>

<style lang="scss" scoped>
.view-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.sactivitylist {
  .v-data-table-header {
    margin-bottom: -2px;
  }
}

.loading-container {
  background: rgba(255,255,255, 0.8);
}

</style>
