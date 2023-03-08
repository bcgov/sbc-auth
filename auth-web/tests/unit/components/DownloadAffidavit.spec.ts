
import { createLocalVue, shallowMount } from '@vue/test-utils'

import DownloadAffidavit from '@/components/auth/staff/review-task/DownloadAffidavit.vue'

import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('DownloadAffidavit.vue', () => {
  let wrapper: any
  let wrapperFactory: any
  const props = {
    tabNumber: 1,
    title: 'Download Affidavit',
    affidavitName: 'test affidavit'
  }

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({
      strict: false
    })

    wrapperFactory = (propsData) => {
      return shallowMount(DownloadAffidavit, {
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
    expect(wrapper).toBeTruthy()
  })

  it('renders the components properly ', () => {
    expect(wrapper.find(DownloadAffidavit).exists()).toBe(true)
  })

  it('renders proper header content', () => {
    expect(wrapper.find('h2').text()).toBe(`${props.tabNumber}. ${props.title}`)
  })
})
