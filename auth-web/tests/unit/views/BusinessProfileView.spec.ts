import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import BusinessProfileView from '@/views/auth/BusinessProfileView.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import { useBusinessStore } from '@/stores/business'

Vue.use(Vuetify)
Vue.use(VueRouter)

vi.mock('../../../src/services/bcol.services')

describe('BusinessProfileView.vue', () => {
  let wrapper: Wrapper<BusinessProfileView>
  const ob = {
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1',
    'AUTH_API_URL': 'https://auth-api-post-dev.pathfinder.gov.bc.ca/api/v1',
    'LEGAL_API_URL': 'https://legal-api-dev.pathfinder.gov.bc.ca/api/v1',
    'VUE_APP_FLAVOR': 'post-mvp'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(ob)
  beforeEach(() => {
    const localVue = createLocalVue()
    const businessStore = useBusinessStore()
    businessStore.currentBusiness = {
      businessIdentifier: 'CP0001245',
      businessNumber: '791861073BC0001',
      created: '2019-08-26T11:50:32.620965+00:00',
      created_by: 'BCREGTEST Jeong SIX',
      id: 11,
      modified: '2019-08-26T11:50:32.620989+00:00',
      name: 'Foobar, Inc.'
    } as any

    wrapper = mount(BusinessProfileView, {
      localVue,
      stubs: {
        BusinessContactForm: true,
        SupportInfoCard: true
      }
    })

    vi.resetModules()
    vi.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })
})
