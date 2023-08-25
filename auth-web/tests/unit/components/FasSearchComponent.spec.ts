import Vue from 'vue'
import Vuetify from 'vuetify'
import initialize from '@/plugins/i18n'
import { mount } from '@vue/test-utils'
import store from '@/stores'

// eslint-disable-next-line sort-imports
import Search from 'fas-ui'

const i18n = initialize(Vue)
Vue.use(Search, { store, i18n })

describe('FasSearchComponent.vue', () => {
  let wrapper: any

  beforeEach(async () => {
    const vuetify = new Vuetify({})

    sessionStorage['FAS_WEB_URL'] = 'https://fas-dev.apps.silver.devops.gov.bc.ca/'
    sessionStorage['PAY_API_URL'] = 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'

    wrapper = mount({ template: `<fas-search-component :isLibraryMode='true'/>` }, {
      i18n,
      vuetify
    })

    vi.resetModules()
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance and has default text', () => {
    expect(wrapper.vm).toBeTruthy()
    // It should display the receipt number, and the no data message at the very least.
    expect(wrapper.find('.header-receiptNumber').text()).toBe('Receipt Number')
    expect(wrapper.find('.no-data').text()).toBe('Search routing slips by entering one of the value above.' +
      ' Click on "columns to show" to add or get rid of additional values.')
  })
})
