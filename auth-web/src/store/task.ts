import { Task, TaskFilterParams } from '@/models/Task'
import { TaskRelationshipStatus, TaskStatus } from '@/util/constants'
import TaskService from '@/services/task.services'
import { defineStore } from 'pinia'
import { reactive } from '@vue/composition-api'

export const useTaskStore = defineStore('task', () => {
  const state = reactive({
    currentTask: {} as Task,
    pendingTasksCount: null as number,
    rejectedTasksCount: null as number
  })

  async function syncTasks () {
    let taskFilter: TaskFilterParams = {
      relationshipStatus: TaskRelationshipStatus.PENDING_STAFF_REVIEW,
      statuses: [TaskStatus.OPEN, TaskStatus.HOLD]
    }
    await fetchTasks(taskFilter)

    taskFilter = {
      relationshipStatus: TaskRelationshipStatus.REJECTED,
      statuses: [TaskStatus.COMPLETED]
    }
    await fetchTasks(taskFilter)
  }

  async function fetchTasks (filterParams: TaskFilterParams) {
    const response = await TaskService.fetchTasks(filterParams)
    if (response?.data) {
      if (filterParams.relationshipStatus === TaskRelationshipStatus.PENDING_STAFF_REVIEW) {
        if (!state.pendingTasksCount) {
          state.pendingTasksCount = response.data.total || 0
        }
      } else if (filterParams.relationshipStatus === TaskRelationshipStatus.REJECTED) {
        if (!state.rejectedTasksCount) {
          state.rejectedTasksCount = response.data.total || 0
        }
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

  async function getTaskById (taskId: number | string): Promise<Task> {
    const response = await TaskService.getTaskById(taskId)
    if (response?.data && response.status === 200) {
      state.currentTask = response.data
      return response.data
    }
  }

  return {
    state,
    fetchTasks,
    getTaskById,
    syncTasks
  }
})
