import { createLocalVue, shallowMount } from '@vue/test-utils'
import AffiliatedEntityTable from '@/components/auth/manage-business/AffiliatedEntityTable.vue'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)
Vue.use(VueI18n)

jest.mock('../../../src/services/user.services')

describe('AffiliatedEntityTable.vue', () => {
  let localVue
  let store

  const config = {
    AUTH_API_URL: 'https://localhost:8080/api/v1/11',
    PAY_API_URL: 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1'
  }

  const businessModule = {
    namespaced: true,
    state: {
      businesses: [{
        'affiliations': [
          5294
        ],
        'businessIdentifier': 'Ty0VnS3JJv',
        'contacts': [

        ],
        'corpType': {
          'code': 'TMP',
          'default': false,
          'desc': 'New Business'
        },
        'created': '2021-08-27T16:36:26.473514',
        'createdBy': 'None None',
        'modified': '2021-08-27T16:36:26.624242',
        'modifiedBy': 'None None',
        'name': 'BEN COMP TEST LIMITED',
        'passCodeClaimed': true
      }]

    },
    action: {
      addBusiness: jest.fn(),
      updateBusinessName: jest.fn(),
      updateFolioNumber: jest.fn()
    }
  }

  const $t = () => ''

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)
  beforeEach(() => {
    localVue = createLocalVue()
    localVue.use(Vuex)

    store = new Vuex.Store({
      strict: false,
      modules: {
        business: businessModule
      }
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('Shows empty panel message if no affiliated entities', () => {
    const wrapper = shallowMount(AffiliatedEntityTable, {
      store,
      localVue,
      propsData: {
        selectedColumns: ['Number', 'Type', 'Status', 'Last Modified', 'Modified By']
      },
      mocks: { $t }
    })
    expect(wrapper.text()).toContain('')
  })

  it('Renders affiliated entity list', async () => {
    const wrapper = shallowMount(AffiliatedEntityTable, {
      store,
      localVue,
      propsData: {
        selectedColumns: ['Number', 'Type', 'Status', 'Last Modified', 'Modified By']
      },
      mocks: { $t }
    })
    await Vue.nextTick()

    expect(wrapper.find('.table-header').text()).toBe('My List (1)')
    expect(wrapper.find('#affiliated-entity-table').exists()).toBe(true)
  })
})
