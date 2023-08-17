import '../test-utils/composition-api-setup' // important to import this first
import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import AffiliatedEntityTable from '@/components/auth/manage-business/AffiliatedEntityTable.vue'
import { BaseVDataTable } from '@/components/datatable'
import { EntityAlertTypes } from '@/util/constants'
import EntityDetails from '@/components/auth/manage-business/EntityDetails.vue'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import { baseVdataTable } from './../test-utils/test-data/baseVdata'
import { businesses } from './../test-utils/test-data/affiliations'
import { getAffiliationTableHeaders } from '@/resources/table-headers'
import { setupIntersectionObserverMock } from '../util/helper-functions'

Vue.use(Vuetify)
Vue.use(VueRouter)
Vue.use(VueI18n)
Vue.use(Vuex)

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

vi.mock('../../../src/services/user.services')

// selectors
const header = baseVdataTable.header
const headerTitles = baseVdataTable.headerTitles
const itemRow = baseVdataTable.itemRow
const itemCell = baseVdataTable.itemCell

businesses.sort((a, b) => {
  if (a.affiliationInvites && !b.affiliationInvites) {
    return -1
  }
  if (!a.affiliationInvites && b.affiliationInvites) {
    return 1
  }
  return 0
})

const businessModule = {
  namespaced: true,
  state: { businesses },
  action: {
    addBusiness: vi.fn(),
    updateBusinessName: vi.fn(),
    updateFolioNumber: vi.fn()
  }
}

const orgModule = {
  namespaced: true,
  state: {
    currentOrganization: {
      name: 'TestMeOut B.C. LTD.',
      id: 3113
    }
  }
}

sessionStorage.setItem('AUTH_API_CONFIG', JSON.stringify({
  AUTH_API_URL: 'https://localhost:8080/api/v1/11',
  PAY_API_URL: 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
}))

const store = new Vuex.Store({
  strict: false,
  modules: {
    business: businessModule,
    org: orgModule
  }
})

const vuetify = new Vuetify({})

describe('AffiliatedEntityTable.vue', () => {
  setupIntersectionObserverMock()
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

    vi.resetModules()
    vi.clearAllMocks()
  })

  it('Renders affiliated entity table', async () => {
    // verify table header
    expect(wrapper.find('.table-header').text()).toBe(`My List (${businesses.length})`)

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

    // startCountAt is offset due to added business with invitations that need to be on top
    const startCountAt = businesses.filter(b => b.affiliationInvites).length

    // first item
    let columns = itemRows.at(startCountAt).findAll(itemCell)
    expect(columns.at(0).text()).toBe('BEN NAME REQUEST LIMITED - PROCESSING')
    expect(columns.at(1).text()).toBe('NR 4045467')
    expect(columns.at(2).text()).toContain('Name Request')
    expect(columns.at(2).text()).toContain('BC Benefit Company')
    expect(columns.at(3).text()).toBe('Processing')
    expect(columns.at(4).text()).toBe('Open')

    // second item
    columns = itemRows.at(startCountAt + 1).findAll(itemCell)
    expect(columns.at(0).text()).toBe('BEN NAME REQUEST LIMITED')
    expect(columns.at(1).text()).toBe('NR 4045466')
    expect(columns.at(2).text()).toContain('Name Request')
    expect(columns.at(2).text()).toContain('BC Benefit Company')
    expect(columns.at(3).text()).toBe('Approved')
    expect(columns.at(4).text()).toBe('Open')

    // third item
    columns = itemRows.at(startCountAt + 2).findAll(itemCell)
    expect(columns.at(0).text()).toBe('BEN NAME REQUEST LIMITED')
    expect(columns.at(1).text()).toBe('NR 4045468')
    expect(columns.at(2).text()).toContain('Name Request')
    expect(columns.at(2).text()).toContain('BC Benefit Company')
    expect(columns.at(3).text()).toBe('Pending Staff Review')
    expect(columns.at(4).text()).toBe('Open')

    // fourth item
    columns = itemRows.at(startCountAt + 3).findAll(itemCell)
    expect(columns.at(0).text()).toBe('')
    expect(columns.at(1).text()).toBe('')
    expect(columns.at(2).text()).toContain('Registration')
    expect(columns.at(2).text()).toContain('BC Benefit Company')
    expect(columns.at(3).text()).toBe('Draft')
    expect(columns.at(4).text()).toBe('Open')

    // fifth item
    columns = itemRows.at(startCountAt + 4).findAll(itemCell)
    expect(columns.at(0).text()).toBe('AC SP 2022.MAY.25 15.38 TEST')
    expect(columns.at(1).text()).toBe('NR 2821990')
    expect(columns.at(2).text()).toContain('Name Request')
    expect(columns.at(2).text()).toContain('BC Sole Proprietorship')
    expect(columns.at(3).text()).toBe('Consumed')
    expect(columns.at(4).text()).toBe('Open')

    // sixth item
    columns = itemRows.at(startCountAt + 5).findAll(itemCell)
    expect(columns.at(0).text()).toBe('Numbered Benefit Company')
    expect(columns.at(1).text()).toBe('Pending')
    expect(columns.at(2).text()).toContain('Incorporation Application')
    expect(columns.at(3).text()).toBe('Draft')
    expect(columns.at(4).text()).toBe('Open')

    expect(wrapper.findComponent(EntityDetails).exists()).toBeTruthy()
    const entityDetails = wrapper.findComponent(EntityDetails)
    expect(entityDetails.exists()).toBeTruthy()
    if (entityDetails.element.parentElement === itemRows.at(5).element) {
      expect(entityDetails.props('details')).toEqual(
        expect.arrayContaining([EntityAlertTypes.FROZEN, EntityAlertTypes.BADSTANDING])
      )
    }
    expect(wrapper.find('.mdi-alert').exists()).toBeTruthy()

    // seventh item
    columns = itemRows.at(startCountAt + 6).findAll(itemCell)
    expect(columns.at(0).text()).toBe('0871095 B.C. LTD.')
    expect(columns.at(1).text()).toBe('BC0871095')
    expect(columns.at(2).text()).toContain('BC Benefit Company')
    expect(columns.at(3).text()).toBe('Historical')
    expect(columns.at(4).text()).toBe('Open')
  })

  it('details for Access Request', async () => {
    const allWithInvites = businesses.filter(b => b.affiliationInvites)
    expect(wrapper.find('#affiliationInvitesStatus').exists()).toBeTruthy()
    expect(wrapper.findAll('#affiliationInvitesStatus').length).toBe(allWithInvites.length)

    // verify correct invites status is being displayed for each business with invites
    const firstAccSingle = allWithInvites[0].affiliationInvites.sort()[0]
    const textSingle = `Request for Authorization to manage from: ${firstAccSingle.fromOrg.name}`
    expect(wrapper.findAll('#affiliationInvitesStatus').at(0).text()).toBe(textSingle)

    const firstAccMulti = allWithInvites[1].affiliationInvites.sort()[0]
    const textMulti = `Request for Authorization to manage from: ${firstAccMulti.fromOrg.name} ` +
      `and ${allWithInvites[1].affiliationInvites.length - 1} other account(s)`
    expect(wrapper.findAll('#affiliationInvitesStatus').at(1).text()).toBe(textMulti)

    // verify elements with invitations are on top
    const allRows = wrapper.findAll('.base-table__item-row')
    expect(allRows.length).toBe(9)

    for (let i = 0; i < allWithInvites.length; i++) {
      // check that all with invites have the entry in table too
      expect(allRows.at(i).html()).toContain('affiliationInvitesStatus')
    }
  })
})
