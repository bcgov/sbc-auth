import { ActivityLog, ActivityLogFilterParams } from '@/models/activityLog'
import ActivityService from '@/services/activityLog.services'
import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'

@Module({ namespaced: true })
export default class ActvityLogModule extends VuexModule {
    currentOrgActivity: ActivityLog

    @Mutation
    public setCurrentOrgActivityLog (activityLog: ActivityLog) {
      this.currentOrgActivity = activityLog
    }

    @Action({ commit: 'setCurrentOrgActivityLog', rawError: true })
    public async getActivityLog (filterParams:ActivityLogFilterParams): Promise<ActivityLog> {
      const { orgId } = filterParams
      if (orgId) {
        const response = await ActivityService.getActivityListByorgId(orgId, filterParams)
        if (response && response.data && response.status === 200) {
          return response.data
        }
      }
      return {}
    }
}
