import { createLocalVue, mount } from '@vue/test-utils'
import AffiliatedEntityTable from '@/components/auth/manage-business/AffiliatedEntityTable.vue'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)
Vue.use(VueI18n)
Vue.use(Vuex)

jest.mock('../../../src/services/user.services')

const businesses = [
  // BEN Name Request
  {
    affiliations: [9752],
    businessIdentifier: 'NR 4045466',
    contacts: [],
    corpType: {
      code: 'NR',
      default: false,
      desc: 'Name Request'
    },
    created: '2022-11-02T19:36:29+00:00',
    lastModified: '2022-11-02T19:37:11+00:00',
    modified: '2022-11-02T19:42:13+00:00',
    modifiedBy: 'BCREGTEST Lucille TWENTY',
    name: 'BEN NAME REQUEST LIMITED',
    // "nameRequest" is usually populated by syncBusinesses():
    nameRequest: {
      legalType: 'BEN',
      names: [{ name: 'BEN NAME REQUEST LIMITED' }],
      nrNumber: 'NR 4045466',
      state: 'APPROVED'
    },
    passCodeClaimed: true,
    status: 'APPROVED'
  },
  // BEN Incorporation Application (named)
  {
    affiliations: [10073],
    businessIdentifier: 'TrHrdmggWI',
    contacts: [],
    corpSubType: {
      code: 'BEN',
      default: false,
      desc: 'Benefit Company'
    },
    corpType: {
      code: 'TMP',
      default: false,
      desc: 'New Business'
    },
    created: '2022-11-16T23:24:09+00:00',
    createdBy: 'None None',
    modified: '2022-11-16T23:24:09+00:00',
    modifiedBy: 'None None',
    name: 'MY BENEFIT COMPANY CORP.',
    nrNumber: 'NR 4045466',
    passCodeClaimed: true
  },
  // BEN Incorporation Application (numbered)
  {
    affiliations: [10075],
    businessIdentifier: 'TMiQaT1iMe',
    contacts: [],
    corpSubType: {
      code: 'BEN',
      default: false,
      desc: 'Benefit Company'
    },
    corpType: {
      code: 'TMP',
      default: false,
      desc: 'New Business'
    },
    created: '2022-11-16T23:27:51+00:00',
    createdBy: 'None None',
    modified: '2022-11-16T23:27:51+00:00',
    modifiedBy: 'None None',
    name: 'TMiQaT1iMe',
    passCodeClaimed: true
  },
  // SP Registration
  {
    affiliations: [10069],
    businessIdentifier: 'TMcftP9uSH',
    contacts: [],
    corpSubType: {
      code: 'SP',
      default: false,
      desc: 'Sole Proprietorship'
    },
    corpType: {
      code: 'RTMP',
      default: false,
      desc: null
    },
    created: '2022-11-16T21:18:41+00:00',
    createdBy: 'None None',
    modified: '2022-11-16T21:18:42+00:00',
    modifiedBy: 'None None',
    name: 'MY SOLE PROPRIETORSHIP',
    nrNumber: 'NR 5938962',
    passCodeClaimed: true
  }
]

const businessModule = {
  namespaced: true,
  state: { businesses },
  action: {
    addBusiness: jest.fn(),
    updateBusinessName: jest.fn(),
    updateFolioNumber: jest.fn()
  }
}

sessionStorage.setItem('AUTH_API_CONFIG', JSON.stringify({
  AUTH_API_URL: 'https://localhost:8080/api/v1/11',
  PAY_API_URL: 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
}))

const localVue = createLocalVue()
localVue.use(Vuex)

const store = new Vuex.Store({
  strict: false,
  modules: {
    business: businessModule
  }
})

const vuetify = new Vuetify()

describe('AffiliatedEntityTable.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(AffiliatedEntityTable, {
      store,
      localVue,
      vuetify,
      propsData: { selectedColumns: ['Number', 'Type', 'Status'] },
      mocks: { $t: () => '' }
    })
  })

  afterEach(() => {
    wrapper.destroy()

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('Renders affiliated entity table', () => {
    // verify table header
    expect(wrapper.find('.table-header').text()).toBe('My List (4)')

    // verify table
    expect(wrapper.find('#affiliated-entity-table').exists()).toBe(true)
    const titles = wrapper.findAll('.v-data-table__wrapper thead span')
    expect(titles.at(0).text()).toBe('Business Name')
    expect(titles.at(1).text()).toBe('Number')
    expect(titles.at(2).text()).toBe('Type')
    expect(titles.at(3).text()).toBe('Status')
    expect(titles.at(4).text()).toBe('Actions')

    // verify table data
    const rows = wrapper.findAll('.v-data-table__wrapper tbody tr')

    // first item
    let columns = rows.at(0).findAll('td')
    expect(columns.at(0).text()).toBe('BEN NAME REQUEST LIMITED')
    expect(columns.at(1).text()).toBe('NR 4045466')
    expect(columns.at(2).text()).toContain('Name Request')
    expect(columns.at(2).text()).toContain('BC Benefit Company')
    expect(columns.at(3).text()).toBe('Approved')
    expect(columns.at(4).text()).toBe('Open')

    // second item
    columns = rows.at(1).findAll('td')
    expect(columns.at(0).text()).toBe('MY BENEFIT COMPANY CORP.')
    expect(columns.at(1).text()).toBe('NR 4045466')
    expect(columns.at(2).text()).toContain('Incorporation Application')
    expect(columns.at(2).text()).toContain('BC Benefit Company')
    expect(columns.at(3).text()).toBe('Draft')
    expect(columns.at(4).text()).toBe('Open')

    // third item
    columns = rows.at(2).findAll('td')
    expect(columns.at(0).text()).toBe('Numbered Benefit Company')
    expect(columns.at(1).text()).toBe('Pending')
    expect(columns.at(2).text()).toContain('Incorporation Application')
    expect(columns.at(2).text()).toContain('BC Benefit Company')
    expect(columns.at(3).text()).toBe('Draft')
    expect(columns.at(4).text()).toBe('Open')

    // fourth item
    columns = rows.at(3).findAll('td')
    expect(columns.at(0).text()).toBe('MY SOLE PROPRIETORSHIP')
    expect(columns.at(1).text()).toBe('NR 5938962')
    expect(columns.at(2).text()).toContain('Registration')
    expect(columns.at(2).text()).toContain('BC Sole Proprietorship')
    expect(columns.at(3).text()).toBe('Draft')
    expect(columns.at(4).text()).toBe('Open')
  })
})
