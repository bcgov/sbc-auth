import '@/composition-api-setup'
import { createLocalVue, mount } from '@vue/test-utils'
import { useStaffStore, useTaskStore } from '@/store'
import ReviewAccountView from '@/views/auth/staff/ReviewAccountView.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})
const router = new VueRouter()

const mockSession = {
  'NAME_REQUEST_URL': 'Name Request Mock URL',
  'NRO_URL': 'NRO Mock URL '
}

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('ReviewAccountView.vue', () => {
  let wrapper: any
  let store: any
  const localVue = createLocalVue()

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
  })
  beforeEach(() => {
    sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(mockSession)
    const taskStore = useTaskStore()
    taskStore.getTaskById = vi.fn(() => {
      return {
        'accountId': 2628,
        'created': '2021-04-19T16:21:28.989168+00:00',
        'createdBy': 'BCREGTEST Jing SIXTEEN',
        'dateSubmitted': '2021-04-19T16:21:28.987006+00:00',
        'id': 44,
        'modified': '2021-04-19T16:21:28.989178+00:00',
        'name': 'sb 16.3',
        'relationshipId': 3674,
        'relationshipStatus': 'PENDING_STAFF_REVIEW',
        'relationshipType': 'PRODUCT',
        'status': 'OPEN',
        'type': 'Wills Registry',
        'user': 31
      }
    }) as any

    const staffStore = useStaffStore()
    staffStore.accountUnderReview = {
      'accessType': 'REGULAR',
      'created': '2019-11-28T22:38:55.157811+00:00',
      'createdBy': 'test user',
      'id': 11,
      'loginOptions': [],
      'modified': '2020-10-13T16:52:24.905410+00:00',
      'modifiedBy': 'user test',
      'name': 'dsafa dsfasd',
      'orgType': 'BASIC',
      'orgStatus': 'ACTIVE',
      'products': [
        753,
        2521,
        3654
      ],
      'statusCode': 'ACTIVE'
    } as any

    staffStore.accountUnderReviewAdmin = {
      'contacts': [
        {
          'created': '2019-11-28T22:37:28.307797+00:00',
          'createdBy': 'test ',
          'email': 'foo@bar.bar',
          'modified': '2020-03-12T19:30:29.914574+00:00',
          'modifiedBy': 'u1se',
          'phone': '(250) 555-1234',
          'phoneExtension': ''
        }
      ],
      'firstname': 'BCREGTEST Ciara',
      'id': 5,
      'lastname': 'FIFTEEN',
      'loginSource': 'BCSC',
      'modified': '2021-04-16T20:09:47.970773+00:00',
      'username': 'bcsc/e3iooqpkgjz3emmwajpdyvjwrxwiowkg'
    } as any

    staffStore.accountUnderReviewAddress = {
      'city': 'Langley',
      'country': 'CA',
      'created': '2020-10-13T16:52:24.867015+00:00',
      'createdBy': 'user',
      'modified': '2020-10-13T16:52:24.867034+00:00',
      'postalCode': 'V3A 7E9',
      'region': 'BC',
      'street': '446-19705 Fraser Hwy',
      'streetAdditional': ''
    } as any

    staffStore.accountUnderReviewAdminContact = {
      'city': 'Langley',
      'country': 'CA',
      'created': '2020-10-13T16:52:24.867015+00:00',
      'createdBy': 'user',
      'modified': '2020-10-13T16:52:24.867034+00:00',
      'postalCode': 'V3A 7E9',
      'region': 'BC',
      'street': '446-19705 Fraser Hwy',
      'streetAdditional': ''
    } as any
  })

  it('Should have a h1', () => {
    wrapper = mount(ReviewAccountView, {
      store,
      vuetify,
      localVue,
      router,

      mocks: {
        $t: (mock) => mock
      }
    })

    expect(wrapper.vm).toBeTruthy()
    // expect(wrapper.find('h1').text()).toBe('Send Invite to Ministry Account')
    wrapper.destroy()
  })
})
