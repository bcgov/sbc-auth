
import { createLocalVue, shallowMount } from '@vue/test-utils'

import NotaryInformation from '@/components/auth/staff/review-task/NotaryInformation.vue'

import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('NotaryInformation.vue', () => {
  let wrapper: any
  let wrapperFactory: any
  const props = {
    tabNumber: 5,
    title: 'Notary Information',
    accountNotaryName: 'test notory',
    accountNotaryContact: {
      'city': 'Langley',
      'country': 'CA',
      'created': '2020-10-13T16:52:24.867015+00:00',
      'createdBy': 'staff user',
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
      return shallowMount(NotaryInformation, {
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
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the NotaryInformation properly ', () => {
    expect(wrapper.findComponent(NotaryInformation).exists()).toBe(true)
  })

  it('renders proper header content fro NotaryInformation', () => {
    expect(wrapper.find('h2').text()).toBe(`${props.tabNumber}. ${props.title}`)
  })
})
