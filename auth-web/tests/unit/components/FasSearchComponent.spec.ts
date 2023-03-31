import { createLocalVue, mount } from '@vue/test-utils'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import i18n from '@/plugins/i18n'

// eslint-disable-next-line sort-imports
import Search from 'fas-ui'

Vue.use(Vuetify)
Vue.use(VueI18n)

describe('FasSearchComponent.vue', () => {
  let wrapper: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {}
    })
    localVue.use(Search, { store, i18n })

    const vuetify = new Vuetify({})

    sessionStorage.__STORE__['FAS_WEB_URL'] = 'https://fas-dev.apps.silver.devops.gov.bc.ca/'
    sessionStorage.__STORE__['PAY_API_URL'] = 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'

    wrapper = mount({ template: `<fas-search-component :isLibraryMode='true'/>` }, {
      store,
      i18n,
      localVue,
      vuetify
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance and has default text', () => {
    expect(wrapper.vm).toBeTruthy()
    // It should display the receipt number, and the no data message at the very least.
    expect(wrapper.find('.header-receiptNumber')).toBeTruthy()
    expect(wrapper.find('.no-data')).toBeTruthy()
  })
})
