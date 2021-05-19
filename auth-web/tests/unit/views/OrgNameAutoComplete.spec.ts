import { createLocalVue, mount } from '@vue/test-utils'

import { AutoCompleteResponse } from '@/models/AutoComplete'
import OrgNameAutoComplete from '@/views/auth/OrgNameAutoComplete.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

const mockSession = {
  'NRO_URL': 'Mock NRO URL',
  'NAME_REQUEST_URL': 'Mock Name Request URL'
}

Vue.use(Vuetify)
Vue.use(VueRouter)
document.body.setAttribute('data-app', 'true')

const router = new VueRouter()
const vuetify = new Vuetify({})

describe('OrgNameAutoComplete.vue', () => {
  let wrapper: any
  const testAutoCompleteResponse: AutoCompleteResponse = {
    total: 10,
    results: [
      {
        type: 'name',
        value: 'TEST TEST ULC1',
        score: 66
      },
      {
        type: 'name',
        value: 'TEST TEST ULC2',
        score: 67
      },
      {
        type: 'name',
        value: 'TEST TEST ULC3',
        score: 68
      },
      {
        type: 'name',
        value: 'TEST TEST ULC4',
        score: 60
      },
      {
        type: 'name',
        value: 'TEST TEST ULC4',
        score: 60
      }
    ]
  }

  beforeEach(() => {
    sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(mockSession)
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const orgModule = {
      namespaced: true,
      actions: {
        getOrgNameAutoComplete: jest.fn().mockResolvedValue(testAutoCompleteResponse)
      }
    }

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        org: orgModule
      }
    })

    wrapper = mount(OrgNameAutoComplete, {
      store,
      localVue,
      router,
      vuetify
    })
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })
  it('does not display when inactive', async () => {
    wrapper.setProps({ setAutoCompleteIsActive: false })
    wrapper.setProps({ searchValue: 'test' })
    // 3 ticks: watcher update, method run, results update
    await Vue.nextTick()
    await Vue.nextTick()
    await Vue.nextTick()
    expect(wrapper.find('[data-test="auto-complete-card"]').exists()).toBe(false)
  })
  it('display when active', async () => {
    wrapper.setProps({ setAutoCompleteIsActive: true })
    wrapper.setProps({ searchValue: 'test' })
    await Vue.nextTick()
    await Vue.nextTick()
    await Vue.nextTick()
    expect(wrapper.vm.showAutoComplete).toBeTruthy()
    expect(wrapper.find('[data-test="auto-complete-item-0"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="auto-complete-item-0"]').text()).toBe('TEST TEST ULC1')
    // Assert duplicate value is removed
    expect(testAutoCompleteResponse.results.length).toBe(5)
    expect(wrapper.findAll('.auto-complete-item').length).toBe(4)
  })
})
