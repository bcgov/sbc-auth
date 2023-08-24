import { ActivityLog, ActivityLogFilterParams } from '@/models/activityLog'
import { reactive, toRefs } from '@vue/composition-api'
import ActivityService from '@/services/activityLog.services'
import { defineStore } from 'pinia'

export const useActivityStore = defineStore('activity', () => {
  const state = reactive({
    currentOrgActivity: {} as ActivityLog
  })

  async function getActivityLog (filterParams:ActivityLogFilterParams): Promise<ActivityLog> {
    const { orgId } = filterParams
    if (orgId) {
      const response = await ActivityService.getActivityListByorgId(orgId, filterParams)
      if (response?.data && response.status === 200) {
        state.currentOrgActivity = response.data
        return response.data
      }
    }
    state.currentOrgActivity = {}
    return {}
  }

  function $reset () {
    state.currentOrgActivity = {} as ActivityLog
  }

  return {
    ...toRefs(state),
    getActivityLog,
    $reset
  }
})
