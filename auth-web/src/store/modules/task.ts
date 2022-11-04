import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import { SessionStorageKeys, TaskRelationshipStatus, TaskStatus } from '@/util/constants'
import { Task, TaskFilterParams } from '@/models/Task'
import ConfigHelper from '@/util/config-helper'
import TaskService from '@/services/task.services'

@Module({ namespaced: true })
export default class TaskModule extends VuexModule {
    currentTask: Task
    pendingTasksCount: number = 0
    rejectedTasksCount: number = 0

    @Mutation
    public setCurrentTask (task: Task) {
      this.currentTask = task
    }

    @Mutation
    public setPendingTasksCount (pendingTasksCount: number) {
      this.pendingTasksCount = pendingTasksCount || 0
    }

    @Mutation
    public setRejectedTasksCount (rejectedTasksCount: number) {
      this.rejectedTasksCount = rejectedTasksCount || 0
    }

    @Action({ commit: 'setCurrentTask', rawError: true })
    public async getTaskById (taskId:number): Promise<Task> {
      const response = await TaskService.getTaskById(taskId)
      if (response && response.data && response.status === 200) {
        return response.data
      }
    }

    // TODO: Add a new API call for fetching counts alone to reduce initial overload - For all calls made in StaffAccountManagement
    @Action({ rawError: true })
    public async syncTasks () {
      const rejectedAccountsSearchFilter = ConfigHelper.getFromSession(SessionStorageKeys.RejectedAccountsSearchFilter) || ''
      const pendingAccountsSearchFilter = ConfigHelper.getFromSession(SessionStorageKeys.PendingAccountsSearchFilter) || ''

      if (!pendingAccountsSearchFilter) {
        let taskFilter: TaskFilterParams = {
          relationshipStatus: TaskRelationshipStatus.PENDING_STAFF_REVIEW,
          statuses: [TaskStatus.OPEN, TaskStatus.HOLD]
        }
        await this.context.dispatch('fetchTasks', taskFilter)
      }

      if (!rejectedAccountsSearchFilter) {
        let taskFilter: TaskFilterParams = {
          relationshipStatus: TaskRelationshipStatus.REJECTED,
          statuses: [TaskStatus.COMPLETED]
        }
        await this.context.dispatch('fetchTasks', taskFilter)
      }
    }

    @Action({ rawError: true })
    public async fetchTasks (filterParams: TaskFilterParams) {
      const response = await TaskService.fetchTasks(filterParams)
      if (response?.data) {
        if (filterParams.relationshipStatus === TaskRelationshipStatus.PENDING_STAFF_REVIEW) {
          this.context.commit('setPendingTasksCount', response.data.total)
        } else if (filterParams.relationshipStatus === TaskRelationshipStatus.REJECTED) {
          this.context.commit('setRejectedTasksCount', response.data.total)
        }
        return {
          limit: response.data.limit,
          page: response.data.page,
          total: response.data.total,
          tasks: response.data.tasks
        }
      }
      return {}
    }
}
