import { createLocalVue, mount } from '@vue/test-utils'
import { useActivityStore, useOrgStore } from '@/stores'
import ActivityLog from '@/components/auth/account-settings/activity-log/ActivityLog.vue'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})

describe('Account settings ActivityLog.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  const $t = () => 'test trans data'
  const currentActivity = {
    'activityLogs': [
      {
        'action': 'Created Affiliation',
        'actor': 'bcsc/w7t5pxb56db6tifzgcbosrnv2kq6i3lo',
        'created': '2021-04-29T18:18:37.386859+00:00',
        'id': 5,
        'itemId': '654',
        'itemName': 'HUNTINGTON PLACE HOUSING CO-OPERATIVE',
        'itemType': 'ACCOUNT',
        'modified': '2021-04-29T18:18:37.484371+00:00',
        'orgId': 1132
      }
    ],
    'limit': 10,
    'page': 1,
    'total': 1
  }
  beforeEach(() => {
    const localVue = createLocalVue()
    const activityStore = useActivityStore()
    activityStore.currentOrgActivity = {
      ...currentActivity
    } as any
    activityStore.getActivityLog = vi.fn(() => {
      return currentActivity
    }) as any

    const orgStore = useOrgStore()
    orgStore.currentOrganization = {
      id: 123,
      name: 'test org'
    }
    orgStore.currentMembership = {
      membershipTypeCode: 'ADMIN'
    } as any

    wrapperFactory = (propsData) => {
      return mount(ActivityLog, {
        localVue,
        vuetify,
        mocks: { $t },
        propsData: {
          ...propsData
        }
      })
    }

    wrapper = wrapperFactory({})
  })

  afterEach(() => {
    wrapper.destroy()
    vi.resetModules()
    vi.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the components properly', () => {
    expect(wrapper.findComponent(ActivityLog).exists()).toBe(true)
  })

  it('renders proper header ', () => {
    expect(wrapper.find('h2').text()).toBe('Activity Log')
  })

  it('Should have data table', () => {
    expect(wrapper.find('.activity-list')).toBeTruthy()
  })
})
