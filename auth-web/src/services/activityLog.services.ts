import { ActivityLog, ActivityLogFilterParams } from '@/models/activityLog'

import { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { axios } from '@/util/http-util'

export default class ActivityService {
  public static async getActivityListByorgId (orgId: number, filterParams:ActivityLogFilterParams): Promise<AxiosResponse<ActivityLog>> {
    const params = new URLSearchParams()
    if (filterParams.pageNumber) {
      params.append('page', filterParams.pageNumber.toString())
    }
    if (filterParams.pageLimit) {
      params.append('limit', filterParams.pageLimit.toString())
    }
    const url = `${ConfigHelper.getAuthAPIUrl()}/orgs/${orgId}/activity-logs`
    return axios.get(url, { params })
  }
}
