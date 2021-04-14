import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'

import { Task } from '@/models/task'

import TaskService from '@/services/task.services'

@Module({ namespaced: true })
export default class TaskModule extends VuexModule {
    currentTask: Task

    @Mutation
    public setCurrentTask (task: Task) {
      this.currentTask = task
    }

    @Action({ commit: 'setCurrentTask', rawError: true })
    public async getTaskById (taskId:number): Promise<Task> {
      const response = await TaskService.getTaskById(taskId)
      if (response && response.data && response.status === 200) {
        return response.data
      }
    }
}
