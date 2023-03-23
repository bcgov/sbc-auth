import '../test-utils/composition-api-setup' // important to import this first
import { createLocalVue, mount } from '@vue/test-utils'
import AffiliatedEntityTable from '@/components/auth/manage-business/AffiliatedEntityTable.vue'
import { BaseVDataTable } from '@/components/datatable'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import { getAffiliationTableHeaders } from '@/resources/table-headers'

Vue.use(Vuetify)
Vue.use(VueRouter)
Vue.use(VueI18n)
Vue.use(Vuex)

jest.mock('../../../src/services/user.services')

const businesses = [
  // BEN Name Request - Processing
  {
    businessIdentifier: 'NR 4045467',
    legalType: 'NR',
    name: 'BEN NAME REQUEST LIMITED - PROCESSING',
    nameRequest: {
      legalType: 'BEN',
      names: [{ name: 'BEN NAME REQUEST LIMITED - PROCESSING' }],
      nrNumber: 'NR 4045467',
      state: 'Processing',
      expirationDate: null
    },
    status: 'Processing'
  },
  // BEN Name Request
  {
    businessIdentifier: 'NR 4045466',
    legalType: 'NR',
    created: '2022-11-02T19:36:29+00:00',
    lastModified: '2022-11-02T19:37:11+00:00',
    modified: '2022-11-02T19:42:13+00:00',
    modifiedBy: 'BCREGTEST Lucille TWENTY',
    name: 'BEN NAME REQUEST LIMITED',
    nameRequest: {
      legalType: 'BEN',
      names: [{ name: 'BEN NAME REQUEST LIMITED' }],
      nrNumber: 'NR 4045466',
      state: 'APPROVED',
      expirationDate: '2022-11-02T19:42:13+00:00'
    },
    passCodeClaimed: true,
    status: 'APPROVED'
  },
  // BEN Incorporation Application (numbered)
  {
    'draftType': 'TMP',
    'identifier': 'TIQcIs5qvA',
    'legalType': 'BEN'
  },
  // SP Registration
  {
    'draftType': 'TMP',
    'identifier': 'TKmp4A16B1',
    'legalType': null,
    'nameRequest': {
      'actions': [
        {
          'URL': null,
          'entitiesFilingName': null,
          'filingName': 'Registration',
          'learTemplate': null
        }
      ],
      'applicants': [
        {
          'emailAddress': 'argus@highwaythreesolutions.com',
          'phoneNumber': '250-111-2222'
        }
      ],
      'entityTypeCd': 'FR',
      'expirationDate': '2022-07-21T06:59:00+00:00',
      'id': 2264498,
      'legalType': 'SP',
      'names': [
        {
          'name': 'AC SP 2022.MAY.25 15.38 TEST',
          'state': 'APPROVED'
        }
      ],
      'natureBusinessInfo': 'asdf',
      'nrNum': 'NR 2821990',
      'requestTypeCd': 'FR',
      'stateCd': 'CONSUMED',
      'target': 'lear'
    },
    'nrNumber': 'NR 2821990'
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

// selectors
const header = '.base-table__header'
const headerTitles = `${header}__title`
const itemRow = '.base-table__item-row'
const itemCell = '.base-table__item-cell'

const vuetify = new Vuetify()

describe('AffiliatedEntityTable.vue', () => {
  let wrapper

  const headers = getAffiliationTableHeaders()

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
    expect(wrapper.findComponent(BaseVDataTable).exists()).toBe(true)
    expect(wrapper.findComponent(BaseVDataTable).find(header).exists()).toBe(true)
    const titles = wrapper.findComponent(BaseVDataTable).findAll(headerTitles)
    expect(titles.length).toBe(headers.length)
    expect(wrapper.find('#affiliated-entity-table').exists()).toBe(true)
    expect(titles.at(0).text()).toBe('Business Name')
    expect(titles.at(1).text()).toBe('Number')
    expect(titles.at(2).text()).toBe('Type')
    expect(titles.at(3).text()).toBe('Status')
    expect(titles.at(4).text()).toBe('Actions')

    // verify table data
    const itemRows = wrapper.findComponent(BaseVDataTable).findAll(itemRow)
    expect(itemRows.length).toBe(businesses.length)

    // first item
    let columns = itemRows.at(0).findAll(itemCell)
    // expect(columns.at(0).text()).toBe('BEN NAME REQUEST LIMITED - PROCESSING')
    // expect(columns.at(1).text()).toBe('NR 4045467')
    // expect(columns.at(2).text()).toContain('Name Request')
    // expect(columns.at(2).text()).toContain('BC Benefit Company')
    // expect(columns.at(3).text()).toBe('Processing')
    // expect(columns.at(4).text()).toBe('Open')

    // // second item
    // columns = rows.at(1).findAll('td')
    // expect(columns.at(0).text()).toBe('BEN NAME REQUEST LIMITED')
    // expect(columns.at(1).text()).toBe('NR 4045466')
    // expect(columns.at(2).text()).toContain('Name Request')
    // expect(columns.at(2).text()).toContain('BC Benefit Company')
    // expect(columns.at(3).text()).toBe('Approved')
    // expect(columns.at(4).text()).toBe('Open')

    // // third item
    // columns = rows.at(2).findAll('td')
    // expect(columns.at(0).text()).toBe('MY BENEFIT COMPANY CORP.')
    // expect(columns.at(1).text()).toBe('TrHrdmggWI')
    // expect(columns.at(2).text()).toContain('Incorporation Application')
    // expect(columns.at(2).text()).toContain('BC Benefit Company')
    // expect(columns.at(3).text()).toBe('Draft')
    // expect(columns.at(4).text()).toBe('Open')

    // // fourth item
    columns = itemRows.at(2).findAll(itemCell)
    expect(columns.at(0).text()).toBe('Numbered Benefit Company')
    expect(columns.at(1).text()).toBe('Pending')
    expect(columns.at(2).text()).toContain('Incorporation Application')
    expect(columns.at(2).text()).toContain('BC Benefit Company')
    expect(columns.at(3).text()).toBe('Draft')
    expect(columns.at(4).text()).toBe('Open')

    // fifth item
    columns = itemRows.at(3).findAll(itemCell)
    expect(columns.at(0).text()).toBe('AC SP 2022.MAY.25 15.38 TEST')
    expect(columns.at(1).text()).toBe('')
    expect(columns.at(2).text()).toContain('Name Request')
    expect(columns.at(2).text()).toContain('BC Sole Proprietorship')
    expect(columns.at(3).text()).toBe('Unknown')
    expect(columns.at(4).text()).toBe('Open')
  })
})
