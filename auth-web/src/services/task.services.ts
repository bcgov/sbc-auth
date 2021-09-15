import { Task, TaskFilterParams, TaskList } from '@/models/Task'

import { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { TaskRelationshipStatus } from '@/util/constants'
import { axios } from '@/util/http-util'

export default class TaskService {
  public static async getTaskById (taskId: number): Promise<AxiosResponse<Task>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/tasks/${taskId}`)
  }

  public static async fetchTasks (taskFilter?: TaskFilterParams): Promise<AxiosResponse<TaskList>> {
    let params = new URLSearchParams()
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

    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/tasks`, { params })
  }

  static async approvePendingTask (task:any): Promise<AxiosResponse> {
    const taskId = task.id
    return axios.put(`${ConfigHelper.getAuthAPIUrl()}/tasks/${taskId}`, { relationshipStatus: TaskRelationshipStatus.ACTIVE })
  }

  static async rejectPendingTask (taskId:any): Promise<AxiosResponse> {
    return axios.put(`${ConfigHelper.getAuthAPIUrl()}/tasks/${taskId}`, { relationshipStatus: TaskRelationshipStatus.REJECTED })
  }

  static async onHoldPendingTask (taskId, remarks:string[]): Promise<AxiosResponse> {
    return axios.put(`${ConfigHelper.getAuthAPIUrl()}/tasks/${taskId}`,
      { status: TaskRelationshipStatus.HOLD, remarks, relationshipStatus: TaskRelationshipStatus.PENDING_STAFF_REVIEW })
  }
}
