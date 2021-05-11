import { createLocalVue, mount } from '@vue/test-utils'

import { AutoCompleteResponseIF } from '@/models/AutoComplete'
import AutoCompleteView from '@/views/auth/AutoCompleteView.vue'
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

describe('AutoCompleteView.vue', () => {
  let wrapper: any
  const testAutoCompleteResponse: AutoCompleteResponseIF = {
    total: 1,
    results: [
      {
        type: 'name',
        value: 'TEST TEST ULC',
        score: 66
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
        getAutoComplete: jest.fn().mockResolvedValue(testAutoCompleteResponse)
      }
    }

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        org: orgModule
      }
    })

    wrapper = mount(AutoCompleteView, {
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
    expect(wrapper.find('[data-test="auto-complete-item-0"]').text()).toBe('TEST TEST ULC')
  })
})
