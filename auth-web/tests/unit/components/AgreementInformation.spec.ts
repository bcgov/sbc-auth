
import { createLocalVue, shallowMount } from '@vue/test-utils'

import AgreementInformation from '@/components/auth/staff/review-task/AgreementInformation.vue'

import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('AgreementInformation.vue', () => {
  let wrapper: any
  let wrapperFactory: any
  const props = {
    tabNumber: 2,
    title: 'Account Information',
    userName: 'user1',
    orgName: 'testorg',
    isTOSAlreadyAccepted: false,
    isApprovalFlow: true
  }

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({
      strict: false
    })

    wrapperFactory = (propsData) => {
      return shallowMount(AgreementInformation, {
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

  it('renders the AgreementInformation components properly ', () => {
    expect(wrapper.findComponent(AgreementInformation).exists()).toBe(true)
  })

  it('renders proper header content', () => {
    expect(wrapper.find('h2').text()).toBe(`${props.tabNumber}. ${props.title}`)
  })
})
