import '../test-utils/composition-api-setup' // important to import this first
import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import AffiliatedEntityTable from '@/components/auth/manage-business/AffiliatedEntityTable.vue'
import { BaseVDataTable } from '@/components/datatable'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import { baseVdataTable } from './../test-utils/test-data/baseVdata'
import { businesses } from './../test-utils/test-data/affiliations'
import { getAffiliationTableHeaders } from '@/resources/table-headers'

Vue.use(Vuetify)
Vue.use(VueRouter)
Vue.use(VueI18n)
Vue.use(Vuex)

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

jest.mock('../../../src/services/user.services')

// selectors
const header = baseVdataTable.header
const headerTitles = baseVdataTable.headerTitles
const itemRow = baseVdataTable.itemRow
const itemCell = baseVdataTable.itemCell

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

const store = new Vuex.Store({
  strict: false,
  modules: {
    business: businessModule
  }
})

const vuetify = new Vuetify({})

describe('AffiliatedEntityTable.vue', () => {
  let wrapper: Wrapper<any>

  const headers = getAffiliationTableHeaders(['Number', 'Type', 'Status'])

  beforeEach(async () => {
    const localVue = createLocalVue()
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

  it('Renders affiliated entity table', async () => {
    // verify table header
    expect(wrapper.find('.table-header').text()).toBe('My List (5)')

    // Wait for the component to render after any state changes
    await wrapper.vm.$nextTick()

    // verify table
    expect(wrapper.findComponent(BaseVDataTable).exists()).toBe(true)
    expect(wrapper.findComponent(BaseVDataTable).find(header).exists()).toBe(true)
    expect(wrapper.find('#affiliated-entity-table').exists()).toBe(true)
    expect(wrapper.find('.v-data-table__wrapper').exists()).toBe(true)
    const titles = wrapper.findComponent(BaseVDataTable).findAll(headerTitles)
    expect(titles.length).toBe(headers.length)
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
    expect(columns.at(0).text()).toBe('BEN NAME REQUEST LIMITED - PROCESSING')
    expect(columns.at(1).text()).toBe('NR 4045467')
    expect(columns.at(2).text()).toContain('Name Request')
    expect(columns.at(2).text()).toContain('BC Benefit Company')
    expect(columns.at(3).text()).toBe('Processing')
    expect(columns.at(4).text()).toBe('Open')

    // second item
    columns = itemRows.at(1).findAll(itemCell)
    expect(columns.at(0).text()).toBe('BEN NAME REQUEST LIMITED')
    expect(columns.at(1).text()).toBe('NR 4045466')
    expect(columns.at(2).text()).toContain('Name Request')
    expect(columns.at(2).text()).toContain('BC Benefit Company')
    expect(columns.at(3).text()).toBe('Approved')
    expect(columns.at(4).text()).toBe('Open')

    // third item
    columns = itemRows.at(2).findAll(itemCell)
    expect(columns.at(0).text()).toBe('BEN NAME REQUEST LIMITED')
    expect(columns.at(1).text()).toBe('NR 4045467')
    expect(columns.at(2).text()).toContain('Name Request')
    expect(columns.at(2).text()).toContain('BC Benefit Company')
    expect(columns.at(3).text()).toBe('Draft')
    expect(columns.at(4).text()).toBe('Open')

    // fourth item
    columns = itemRows.at(3).findAll(itemCell)
    expect(columns.at(0).text()).toBe('Numbered Benefit Company')
    expect(columns.at(1).text()).toBe('Pending')
    expect(columns.at(2).text()).toContain('Incorporation Application')
    expect(columns.at(2).text()).toContain('BC Benefit Company')
    expect(columns.at(3).text()).toBe('Draft')
    expect(columns.at(4).text()).toBe('Open')

    // fifth item
    columns = itemRows.at(4).findAll(itemCell)
    expect(columns.at(0).text()).toBe('AC SP 2022.MAY.25 15.38 TEST')
    expect(columns.at(1).text()).toBe('Pending')
    expect(columns.at(2).text()).toContain('Name Request')
    expect(columns.at(2).text()).toContain('BC Sole Proprietorship')
    expect(columns.at(3).text()).toBe('Consumed')
    expect(columns.at(4).text()).toBe('Open')
  })
})
