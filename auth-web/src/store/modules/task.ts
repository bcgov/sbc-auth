import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import { Task, TaskFilterParams } from '@/models/Task'

import TaskService from '@/services/task.services'

@Module({ namespaced: true })
export default class TaskModule extends VuexModule {
    currentTask: Task
    totalStaffTasks: number

    @Mutation
    public setCurrentTask (task: Task) {
      this.currentTask = task
    }

    @Mutation
    public setTotalStaffTasks (totalStaffTasks: number) {
      this.totalStaffTasks = totalStaffTasks
    }

    @Action({ commit: 'setCurrentTask', rawError: true })
    public async getTaskById (taskId:number): Promise<Task> {
      const response = await TaskService.getTaskById(taskId)
      if (response && response.data && response.status === 200) {
        return response.data
      }
    }

    @Action({ rawError: true })
    public async fetchTasks (filterParams: TaskFilterParams) {
      const response = await TaskService.fetchTasks(filterParams)
      if (response?.data) {
        this.context.commit('setTotalStaffTasks', response.data.total)
        return {
          limit: response.data.limit,
          page: response.data.page,
          total: response.data.total,
          tasks: response.data.tasks
        }
      }
      this.context.commit('setTotalStaffTasks', 0)
      return {}
    }
}
