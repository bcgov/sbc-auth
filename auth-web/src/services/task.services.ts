import { Task, TaskFilterParams, TaskList } from '@/models/Task'
import { TaskRelationshipStatus, TaskType } from '@/util/constants'

import { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { axios } from '@/util/http-util'

export default class TaskService {
  public static async getTaskById (taskId: number | string): Promise<AxiosResponse<Task>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/tasks/${taskId}`)
  }

  public static async fetchTasks (taskFilter?: TaskFilterParams): Promise<AxiosResponse<TaskList>> {
    const params = new URLSearchParams()
    if (taskFilter.relationshipStatus) {
      params.append('relationshipStatus', taskFilter.relationshipStatus)
    }
    if (taskFilter.statuses) {
      taskFilter.statuses.forEach(status =>
        params.append('status', status))
    }
    if (taskFilter.type) {
      params.append('type', taskFilter.type)
    }
    if (taskFilter.pageNumber) {
      params.append('page', taskFilter.pageNumber.toString())
    }
    if (taskFilter.pageLimit) {
      params.append('limit', taskFilter.pageLimit.toString())
    }
    if (taskFilter.name) {
      params.append('name', taskFilter.name)
    }
    if (taskFilter.startDate) {
      params.append('startDate', taskFilter.startDate)
    }
    if (taskFilter.endDate) {
      params.append('endDate', taskFilter.endDate)
    }
    if (taskFilter.modifiedBy) {
      params.append('modifiedBy', taskFilter.modifiedBy)
    }

    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/tasks`, { params })
  }

  static async approvePendingTask (task:any): Promise<AxiosResponse> {
    const taskId = task.id
    return axios.put(`${ConfigHelper.getAuthAPIUrl()}/tasks/${taskId}`,
      { relationshipStatus: TaskRelationshipStatus.ACTIVE })
  }

  static async rejectPendingTask (taskId:any, remarks:string[] = []): Promise<AxiosResponse> {
    return axios.put(`${ConfigHelper.getAuthAPIUrl()}/tasks/${taskId}`,
      { remarks, relationshipStatus: TaskRelationshipStatus.REJECTED })
  }

  static async onHoldPendingTask (taskId, remarks:string[]): Promise<AxiosResponse> {
    return axios.put(`${ConfigHelper.getAuthAPIUrl()}/tasks/${taskId}`,
      { status: TaskRelationshipStatus.HOLD, remarks, relationshipStatus: TaskRelationshipStatus.PENDING_STAFF_REVIEW })
  }

  public static async getQsApplicantForTaskReview (accountId: number | string, type: TaskType): Promise<AxiosResponse> {
    const apiKey = ConfigHelper.getMhrAPIKey()
    const headers = {
      'x-apikey': apiKey,
      'Account-Id': accountId
    }
    const url = type === TaskType.MHR_MANUFACTURERS
      ? `${ConfigHelper.getMhrAPIUrl()}/manufacturers`
      : `${ConfigHelper.getMhrAPIUrl()}/qualified-suppliers`

    return axios.get(url, { headers })
  }
}
