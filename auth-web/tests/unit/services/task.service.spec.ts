import { Task } from '@/models/Task'
import TaskService from '../../../src/services/task.services'
import axios from 'axios'

var mockob = {
  'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1',
  'AUTH_API_URL': 'https://auth-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
}
const task: Task[] = [{
  'accountId': 2628,
  'created': new Date('2021-04-19T16:21:28.989168+00:00'),
  'createdBy': 'BCREGTEST Jing SIXTEEN',
  'dateSubmitted': new Date('2021-04-19T16:22:28.989168+00:00'),
  'id': 44,
  'modified': new Date('2021-04-19T16:23:28.989168+00:00'),
  'name': 'sb 16.3',
  'relationshipId': 3674,
  'relationshipStatus': 'PENDING_STAFF_REVIEW',
  'relationshipType': 'PRODUCT',
  'status': 'OPEN',
  'type': 'Wills Registry'
}]

describe('Task service', () => {
  beforeEach(() => {
    sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockob)
    // @ts-ignore
    jest.clearAllMocks()
  })

  it('call getTaskById() for task Details ', () => {
    jest.mock('axios')

    const resp = { data: task }
    axios.get = jest.fn().mockReturnValue(resp)

    TaskService.getTaskById(1).then((response) => {
      expect(response).toEqual(task)
    })
  })
  it('call fetchTasks() for all tasks  ', () => {
    jest.mock('axios')

    const resp = { data: task }
    axios.get = jest.fn().mockReturnValue(resp)
    const taskFilter = {
      status: 'PENDING_STAFF_REVIEW',
      type: 'OPEN',
      pageNumber: 1,
      pageLimit: 10
    }

    TaskService.fetchTasks(taskFilter).then((response) => {
      expect(response).toEqual(task)
    })
  })

  it('call approvePendingTask() to approve request ', async () => {
    jest.mock('axios')
    const resp = { data: task }
    axios.put = jest.fn().mockReturnValue(resp)

    TaskService.approvePendingTask(task).then((response) => {
      expect(response).toEqual(task)
    })
  })

  it('call rejectPendingTask() to reject request ', async () => {
    jest.mock('axios')

    const resp = { data: task }
    axios.put = jest.fn().mockReturnValue(resp)

    TaskService.rejectPendingTask(task).then((response) => {
      expect(response).toEqual(task)
    })
  })
})
