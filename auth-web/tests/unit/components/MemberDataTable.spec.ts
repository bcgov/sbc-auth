import { createLocalVue, mount } from '@vue/test-utils'
import { useOrgStore, useUserStore } from '@/stores'
import MemberDataTable from '@/components/auth/account-settings/team-management/MemberDataTable.vue'
import OrgService from '../../../src/services/org.services'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})

vi.mock('../../../src/services/bcol.services')

const membersList = [{
  'id': 2909,
  'membershipStatus': 'ACTIVE',
  'membershipTypeCode': 'USER',
  'user': {
    'contacts': [
      {
        'created': '2020-02-12T21:45:01.285260+00:00',
        'createdBy': 'BCREGTEST Delbert TWENTYFIVE',
        'email': 'foo@bar.com',
        'links': [
          128
        ],
        'modified': '2020-02-12T21:45:01.285278+00:00',
        'phone': '',
        'phoneExtension': '',
        'versions': []
      }
    ],
    'firstname': 'BCREGTEST Delbert',
    'id': 20,
    'lastname': 'TWENTYFIVE',
    'loginSource': 'BCSC',
    'modified': '2020-08-25T20:43:13.232326+00:00',
    'username': 'bcsc/malpaovmqyxtxfdu47z54mwswuerbdni'
  }
},
{
  'id': 2906,
  'membershipStatus': 'ACTIVE',
  'membershipTypeCode': 'COORDINATOR',
  'user': {
    'contacts': [
      {
        'created': '2019-11-28T20:05:54.449895+00:00',
        'createdBy': 'BCREGTEST Bashshar TWENTYTWO',
        'email': 'test@gmail.com',
        'links': [
          12
        ],
        'modified': '2019-12-18T20:54:01.894819+00:00',
        'modifiedBy': 'BCREGTEST Bashshar TWENTYTWO',
        'phone': '',
        'phoneExtension': '57',
        'versions': []
      }
    ],
    'firstname': 'BCREGTEST Bashshar',
    'id': 6,
    'lastname': 'TWENTYTWO',
    'loginSource': 'BCSC',
    'modified': '2020-07-24T22:02:20.312360+00:00',
    'username': 'bcsc/c272kovlg2knludndfrstiklgufitypx'
  }
},
{
  'id': 141,
  'membershipStatus': 'ACTIVE',
  'membershipTypeCode': 'ADMIN',
  'user': {
    'contacts': [
      {
        'created': '2020-05-14T21:12:20.058359+00:00',
        'createdBy': 'BCREGTEST Bena THIRTEEN',
        'email': 'test@test.com',
        'links': [
          714
        ],
        'modified': '2020-07-17T18:04:29.006705+00:00',
        'modifiedBy': 'BCREGTEST Bena THIRTEEN',
        'phone': '(778) 678-9998',
        'phoneExtension': '123',
        'versions': []
      }
    ],
    'firstname': 'BCREGTEST Bena',
    'id': 4,
    'lastname': 'THIRTEEN',
    'loginSource': 'BCSC',
    'modified': '2020-09-08T17:51:29.648717+00:00',
    'username': 'bcsc/fyd76wbcng76cpxbu42hhua4qphtivb5'
  }
}]

const roleInfoList = [
  {
    'default': true,
    'desc': 'Member of the organization',
    'displayName': 'User',
    'displayOrder': 1,
    'icon': 'mdi-account-outline',
    'label': 'Submit searches and filings, add / remove businesses',
    'name': 'USER'
  },
  {
    'default': false,
    'desc': 'Admin for the organization',
    'displayName': 'Account Coordinator',
    'displayOrder': 2,
    'icon': 'mdi-account-cog-outline',
    'label': 'Submit searches and filings, add / remove businesses, add / remove team members',
    'name': 'COORDINATOR'
  },
  {
    'default': false,
    'desc': 'Owner (super-admin) of the organization',
    'displayName': 'Account Administrator',
    'displayOrder': 3,
    'icon': 'mdi-shield-account-outline',
    'label': 'Submit searches and filings, add / remove businesses, add / remove team members,' +
      ' access financial statements, update payment methods',
    'name': 'ADMIN'
  }
]

describe('MemberDataTable.vue', () => {
  let wrapper: any

  const config = {
    AUTH_API_URL: 'https://localhost:8080/api/v1/11',
    PAY_API_URL: 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuetify)
    localVue.use(VueRouter)

    const router = new VueRouter()

    OrgService.getOrgMembers = vi.fn().mockResolvedValue({
      data: {
        members: membersList
      }
    })

    const orgStore = useOrgStore()
    orgStore.pendingOrgInvitations = []
    orgStore.currentOrganization = {} as any
    orgStore.activeOrgMembers = membersList as any
    orgStore.currentMembership = [{
      membershipTypeCode: 'ADMIN',
      membershipStatus: 'ACTIVE',
      user: { username: 'test' }
    }] as any
    const userStore = useUserStore()
    userStore.currentUser = { 'userName': 'test' } as any
    userStore.roleInfos = roleInfoList

    const $t = () => {}

    wrapper = mount(MemberDataTable, {
      localVue,
      router,
      vuetify,
      mocks: { $t }
    })

    vi.resetModules()
    vi.clearAllMocks()
  })
  afterAll(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('mounting works', () => {
    expect(wrapper.find('.member-data-table')).toBeTruthy()
    expect(wrapper.find('.user-name')).toBeTruthy()
  })

  it('renders the correct number of members', () => {
    const selector = '.member-data-table tbody tr'
    const itemsCount = wrapper.vm.$el.querySelectorAll(selector).length
    expect(itemsCount).toEqual(3)
    expect(wrapper.vm.$el.querySelector(selector)).not.toBeNull()
  })

  it('renders members table correctly', () => {
    const items = wrapper.vm.$el.querySelectorAll('.member-data-table tbody tr')
    expect(items[0].querySelector('.user-name').textContent.trim()).toEqual('BCREGTEST Delbert TWENTYFIVE')
    expect(items[0].querySelector('.contact-email').textContent.trim()).toEqual('foo@bar.com')
    expect(items[1].querySelector('.user-name').textContent.trim()).toEqual('BCREGTEST Bashshar TWENTYTWO')
    expect(items[1].querySelector('.contact-email').textContent.trim()).toEqual('test@gmail.com')
  })

  it('renders action buttons in members table correctly', async () => {
    const currentMember = [{
      membershipTypeCode: 'USER',
      membershipStatus: 'ACTIVE',
      user: { username: 'test' }
    }] as any
    useOrgStore().setCurrentMembership(currentMember)
    const items = wrapper.vm.$el.querySelectorAll('.member-data-table tbody tr')
    expect(items[0].querySelector('[title="Remove Team Member"]').style.display).toBe('')
  })
})
