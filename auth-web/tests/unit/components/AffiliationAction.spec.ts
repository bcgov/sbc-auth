import '../test-utils/composition-api-setup' // important to import this first
import { Wrapper, createLocalVue, shallowMount } from '@vue/test-utils'
import AffiliationAction from '@/components/auth/manage-business/AffiliationAction.vue'
import Vuetify from 'vuetify'
import { businesses } from './../test-utils/test-data/affiliations'
import { useBusinessStore } from '@/stores'

vi.mock('../../../src/services/user.services')

const vuetify = new Vuetify({})

sessionStorage.setItem('AUTH_API_CONFIG', JSON.stringify({
  AUTH_API_URL: 'https://localhost:8080/api/v1/11',
  PAY_API_URL: 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
}))

// Note many of the tests for this are in AffiliatedEntityTable.
describe('is a Vue instance', () => {
  let wrapper: Wrapper<any>
  beforeEach(() => {
    const businessStore = useBusinessStore()
    businessStore.businesses = businesses
    const localVue = createLocalVue()
    wrapper = shallowMount(AffiliationAction, {
      localVue,
      vuetify,
      mocks: { $t: () => '' },
      propsData: { item: businesses[0] }
    })
  })

  it('is a Vue Instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })
})
