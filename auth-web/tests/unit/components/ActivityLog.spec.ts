import { createLocalVue, mount } from '@vue/test-utils'

import ActivityLog from '@/components/auth/account-settings/activity-log/ActivityLog.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

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
    localVue.use(Vuex)
    const activityLogModule = {
      namespaced: true,
      state: {
        currentOrgActivity: {
          ...currentActivity
        }
      },
      actions: {
        getActivityLog: vi.fn(() => {
          return currentActivity
        })
      }

    }
    const orgModule = {
      namespaced: true,
      actions: {
        getActivityLog: vi.fn()
      },
      state: {
        currentOrganization: {
          id: 123,
          name: 'test org'
        },
        currentMembership: {
          membershipTypeCode: 'ADMIN'
        }
      }
    }

    const store = new Vuex.Store({
      strict: false,
      modules: {
        org: orgModule,
        activity: activityLogModule
      }
    })

    wrapperFactory = (propsData) => {
      return mount(ActivityLog, {
        store,
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
