import { Member, Organization } from '@/models/Organization'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import Statements from '@/components/auth/account-settings/statement/Statements.vue'
import VueRouter from 'vue-router'
import { useOrgStore } from '@/store/org'

const router = new VueRouter()

describe('Statements.vue', () => {
  let store
  let localVue

  const config = {
    AUTH_API_URL: 'https://localhost:8080/api/v1/sbc',
    PAY_API_URL: 'https://pay.gov.bc.ca/api/v1'
  }
  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    localVue = createLocalVue()

    const orgStore = useOrgStore()
    orgStore.getStatementsList = vi.fn()
    orgStore.getStatement = vi.fn()
    orgStore.currentOrganization = {
      'accessType': 'REGULAR',
      'created': '2021-05-02T20:54:15.936923+00:00',
      'createdBy': 'user1',
      'hasApiAccess': false,
      'id': 124,
      'loginOptions': [],
      'modified': '2021-05-02T20:54:15.936935+00:00',
      'name': 'Org 2',
      'orgType': 'PREMIUM',
      'orgStatus': 'ACTIVE',
      'products': [
        3830,
        3831,
        3832,
        3833,
        3834
      ],
      'statusCode': 'ACTIVE',
      'bcolAccountDetails': { accountNumber: '55' }
    } as Organization
    orgStore.currentMembership = {
      'id': 123,
      'membershipStatus': 'ACTIVE',
      'membershipTypeCode': 'ADMIN',
      'user': {
        'contacts': [
          {
            'email': 'test1@test.com',
            'phone': '',
            'phoneExtension': ''
          }
        ],
        'firstname': 'user',
        'id': 4,
        'lastname': 'one',
        'loginSource': 'BCSC',
        'username': 'user1'
      }
    } as Member

    vi.resetModules()
    vi.clearAllMocks()
  })

  it('is a Vue instance', () => {
    const $t = () => ''
    const wrapper = shallowMount(Statements, {
      store,
      localVue,
      router,
      mocks: { $t }
    })
    expect(wrapper.vm).toBeTruthy()
    wrapper.destroy()
  })

  it('renders proper header content', () => {
    const $t = () => ''
    const wrapper = shallowMount(Statements, {
      store,
      localVue,
      router,
      mocks: { $t }
    })
    expect(wrapper.find('h2').text()).toBe('Statements')
    wrapper.destroy()
  })
})
