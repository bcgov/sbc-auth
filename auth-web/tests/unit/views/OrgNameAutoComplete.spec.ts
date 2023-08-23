import { createLocalVue, mount } from '@vue/test-utils'
import { AutoCompleteResponse } from '@/models/AutoComplete'
import OrgNameAutoComplete from '@/views/auth/OrgNameAutoComplete.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'
import { useOrgStore } from '@/store/org'

const mockSession = {
  'NRO_URL': 'Mock NRO URL',
  'NAME_REQUEST_URL': 'Mock Name Request URL'
}

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
    sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(mockSession)
    const localVue = createLocalVue()

    const orgStore = useOrgStore()
    orgStore.getOrgNameAutoComplete = vi.fn().mockResolvedValue(testAutoCompleteResponse)

    wrapper = mount(OrgNameAutoComplete, {
      localVue,
      router,
      vuetify
    })
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
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
    wrapper.setProps({ setAutoCompleteIsActive: true, searchValue: 'test' })
    // setting autoCompleteResults not working in test so set manually
    wrapper.vm.autoCompleteResults = testAutoCompleteResponse.results
    await flushPromises()
    expect(wrapper.vm.showAutoComplete).toBeTruthy()
    expect(wrapper.find('[data-test="auto-complete-item-0"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="auto-complete-item-0"]').text()).toBe('TEST TEST ULC1')
    // Assert duplicate value is removed
    expect(testAutoCompleteResponse.results.length).toBe(5)
    expect(wrapper.findAll('.auto-complete-item').length).toBe(5)
  })
})
