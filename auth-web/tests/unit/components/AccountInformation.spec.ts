
import { createLocalVue, shallowMount } from '@vue/test-utils'

import AccountInformation from '@/components/auth/staff/review-task/AccountInformation.vue'

import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('AccountInformation.vue', () => {
  let wrapper: any
  let wrapperFactory: any
  const props = {
    tabNumber: 2,
    title: 'Account Information',
    accountUnderReview: {
      'accessType': 'REGULAR',
      'created': '2019-11-28T22:38:55.157811+00:00',
      'createdBy': 'user1',
      'id': 11,
      'loginOptions': [],
      'modified': '2020-10-13T16:52:24.905410+00:00',
      'modifiedBy': 'user 2',
      'name': 'dsafa dsfasd',
      'orgType': 'BASIC',
      'orgStatus': 'ACTIVE',
      'products': [
        753,
        2521,
        3654
      ],
      'statusCode': 'ACTIVE'
    },
    accountUnderReviewAddress: {
      'city': 'Langley',
      'country': 'CA',
      'created': '2020-10-13T16:52:24.867015+00:00',
      'createdBy': 'user 1',
      'modified': '2020-10-13T16:52:24.867034+00:00',
      'postalCode': 'V3A 7E9',
      'region': 'BC',
      'street': '446-19705 Fraser Hwy',
      'streetAdditional': ''
    }

  }

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({
      strict: false
    })

    wrapperFactory = (propsData) => {
      return shallowMount(AccountInformation, {
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
    expect(wrapper.find(AccountInformation).exists()).toBe(true)
  })

  it('renders proper header content', () => {
    expect(wrapper.find('h2').text()).toBe(`${props.tabNumber}. ${props.title}`)
  })
})
