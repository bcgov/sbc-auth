import { createLocalVue, mount } from '@vue/test-utils'

import IncorporationSearchResultView from '@/views/auth/staff/IncorporationSearchResultView.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import { useBusinessStore } from '@/store/business'

const vuetify = new Vuetify({})
const router = new VueRouter()

const mockSession = {
  'NRO_URL': 'Mock NRO URL',
  'NAME_REQUEST_URL': 'Mock Name Request URL'
}

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('IncorporationSearchResultView.vue', () => {
  let wrapper: any
  const localVue = createLocalVue()

  const businessStore = useBusinessStore()
  businessStore.currentBusiness = {
    name: 'affiliated_test_business',
    businessIdentifier: '123123',
    businessNumber: '1231231'
  } as any

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  beforeEach(() => {
    sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(mockSession)
  })

  it('Search Result with affiliated CP is valid', () => {
    wrapper = mount(IncorporationSearchResultView, {
      vuetify,
      localVue,
      router,
      propsData: {
        affiliatedOrg: {
          name: 'test',
          orgType: 'Active',
          accessType: 'Active',
          statusCode: 'Active'
        }
      },
      mocks: {
        $t: (mock) => mock
      }
    })

    const searchResult = wrapper.vm.searchResult

    expect(wrapper.vm).toBeTruthy()
    expect(searchResult[0].businessIdentifier).toBe('123123')
    expect(searchResult[0].businessNumber).toBe('1231231')
    expect(searchResult[0].statusCode).toBe('Active')
    expect(searchResult[0].name).toBe('affiliated_test_business')
    expect(searchResult[0].orgType).toBe('Active')
    expect(searchResult[0].account).toBe('test')
  })

  it('Search Result with unaffiliated CP is valid', () => {
    const businessStore = useBusinessStore()
    businessStore.currentBusiness = {
      name: 'unaffiliated_test_business',
      businessIdentifier: '123123',
      businessNumber: '1231231'
    } as any

    wrapper = mount(IncorporationSearchResultView, {
      localVue,
      router,
      vuetify,
      mocks: {
        $t: (mock) => mock
      }
    })

    const searchResult = wrapper.vm.searchResult
    expect(wrapper.vm.formatType(searchResult[0])).toBe('N/A')
    expect(searchResult[0].name).toBe('unaffiliated_test_business')
    expect(searchResult[0].account).toBe('No Affiliation')
    expect(searchResult[0].businessIdentifier).toBe('123123')
    expect(searchResult[0].businessNumber).toBe('1231231')
  })
})
