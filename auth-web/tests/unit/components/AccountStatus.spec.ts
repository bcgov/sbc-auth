
import { createLocalVue, shallowMount } from '@vue/test-utils'

import AccountStatus from '@/components/auth/staff/review-task/AccountStatus.vue'

import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('AccountStatus.vue', () => {
  let wrapper: any
  let wrapperFactory: any
  const props = {
    tabNumber: 2,
    title: 'Account Information',
    taskDetails: {
      'accountId': 123,
      'created': '2021-04-19T16:21:28.989168+00:00',
      'createdBy': 'staff 1',
      'dateSubmitted': '2021-04-19T16:21:28.987006+00:00',
      'id': 44,
      'modified': '2021-04-19T16:21:28.989178+00:00',
      'name': 'sb 16.3',
      'relationshipId': 3674,
      'relationshipStatus': 'PENDING_STAFF_REVIEW',
      'relationshipType': 'PRODUCT',
      'status': 'OPEN',
      'type': 'Wills Registry',
      'user': 32
    }

  }

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({
      strict: false
    })

    wrapperFactory = (propsData) => {
      return shallowMount(AccountStatus, {
        localVue,
        store,
        vuetify,
        propsData: {
          ...propsData
        }
      })
    }

    wrapper = wrapperFactory(props)
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('renders the components properly ', () => {
    expect(wrapper.find(AccountStatus).exists()).toBe(true)
  })

  it('renders proper header content', () => {
    expect(wrapper.find('h2').text()).toBe(`${props.tabNumber}. ${props.title}`)
  })
})
