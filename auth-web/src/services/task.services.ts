import { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { Task } from '@/models/task'
import { axios } from '@/util/http-util.ts'

export default class TaskService {
  public static async getTaskById (taskId: number): Promise<AxiosResponse<Task>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/tasks/${taskId}`)
  }

  static async approvePendingTask (task:any): Promise<AxiosResponse> {
    const taskId = task.id
    return axios.put(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/tasks/${taskId}`, { ...task, relationshipStatus: 'APPROVED' })
  }

  static async rejectPendingTask (task:any): Promise<AxiosResponse> {
    const taskId = task.id
    return axios.put(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/tasks/${taskId}`, { ...task, relationshipStatus: 'REJECTED' })
  }
}
