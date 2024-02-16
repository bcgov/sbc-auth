import { Task } from '@/models/Task'
import TaskService from '../../../src/services/task.services'

const mockob = {
  'PAY_API_URL': 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1',
  'AUTH_API_URL': 'https://auth-api-dev.silver.devops.gov.bc.ca/api/v1'
}
const mockTask: Task[] = [{
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

const mocks = vi.hoisted(() => ({
  get: vi.fn().mockReturnValue(mockTask),
  put: vi.fn().mockReturnValue(mockTask)
}))

describe('Task service', () => {
  beforeEach(() => {
    sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(mockob)
    vi.doMock('axios', () => {
      return {
        create: () => {
          return {
            get: mocks.get,
            put: mocks.put,
            interceptors: {
              request: { eject: vi.fn(), use: vi.fn() },
              response: { eject: vi.fn(), use: vi.fn() }
            }
          }
        }
      }
    })
    vi.clearAllMocks()
  })

  it('call getTaskById() for task Details ', () => {
    TaskService.getTaskById(1).then((response) => {
      expect(response).toEqual(mockTask)
    })
  })
  it('call fetchTasks() for all tasks  ', () => {
    const taskFilter = {
      status: 'PENDING_STAFF_REVIEW',
      type: 'OPEN',
      pageNumber: 1,
      pageLimit: 10
    }

    TaskService.fetchTasks(taskFilter).then((response) => {
      expect(response).toEqual(mockTask)
    })
  })

  it('call approvePendingTask() to approve request ', async () => {
    TaskService.approvePendingTask(mockTask).then((response) => {
      expect(response).toEqual(mockTask)
    })
  })

  it('call rejectPendingTask() to reject request ', async () => {
    TaskService.rejectPendingTask(mockTask).then((response) => {
      expect(response).toEqual(mockTask)
    })
  })
})
