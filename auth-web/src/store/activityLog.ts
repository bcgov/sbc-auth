import { ActivityLog, ActivityLogFilterParams } from '@/models/activityLog'
import ActivityService from '@/services/activityLog.services'
import { defineStore } from 'pinia'
import { reactive } from '@vue/composition-api'

export const useActivityStore = defineStore('activity', () => {
  const state = reactive({
    currentOrgActivity: {} as ActivityLog
  })

  async function getActivityLog (filterParams:ActivityLogFilterParams): Promise<ActivityLog> {
    const { orgId } = filterParams
    if (orgId) {
      const response = await ActivityService.getActivityListByorgId(orgId, filterParams)
      if (response && response.data && response.status === 200) {
        state.currentOrgActivity = response.data
        return response.data
      }
    }
    state.currentOrgActivity = {}
    return {}
  }

  return {
    state,
    getActivityLog
  }
})
