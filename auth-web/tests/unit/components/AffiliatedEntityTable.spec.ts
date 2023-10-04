import '../test-utils/composition-api-setup' // important to import this first
import { AffiliationInvitationStatus, AffiliationInvitationType, EntityAlertTypes, SessionStorageKeys } from '@/util/constants'
import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import { actions, businesses, moreBusinesses } from './../test-utils/test-data/affiliations'
import { useBusinessStore, useOrgStore } from '@/stores'
import AffiliatedEntityTable from '@/components/auth/manage-business/AffiliatedEntityTable.vue'
import { AffiliationInviteInfo } from '@/models/affiliation'
import { BaseVDataTable } from '@/components/datatable'
import CommonUtils from '@/util/common-util'
import EntityDetails from '@/components/auth/manage-business/EntityDetails.vue'
import { VueConstructor } from 'vue'
import Vuetify from 'vuetify'
import { baseVdataTable } from './../test-utils/test-data/baseVdata'
import { getAffiliationTableHeaders } from '@/resources/table-headers'
import { setupIntersectionObserverMock } from '../util/helper-functions'

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

sessionStorage.setItem('AUTH_API_CONFIG', JSON.stringify({
  AUTH_API_URL: 'https://localhost:8080/api/v1/11',
  PAY_API_URL: 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
}))

const vuetify = new Vuetify({})

describe('AffiliatedEntityTable.vue', () => {
  setupIntersectionObserverMock()
  let wrapper: Wrapper<any>
  let localVue: VueConstructor<any>

  const headers = getAffiliationTableHeaders(['Number', 'Type', 'Status'])

  beforeEach(async () => {
    const localVue = createLocalVue()
    const businessStore = useBusinessStore()
    businessStore.businesses = businesses
    const orgStore = useOrgStore()
    orgStore.currentOrganization = {
      name: 'TestMeOut B.C. LTD.',
      id: 3113
    } as any

    wrapper = mount(AffiliatedEntityTable, {
      localVue,
      vuetify,
      propsData: { selectedColumns: ['Number', 'Type', 'Status'] },
      mocks: { $t: () => '' }
    })
  })

  afterEach(() => {
    wrapper.destroy()
    sessionStorage.clear()

    vi.resetModules()
    vi.clearAllMocks()
  })

  it('Renders affiliated entity table with correct contents', async () => {
    wrapper = mount(AffiliatedEntityTable, {
      localVue,
      vuetify,
      propsData: { selectedColumns: ['Number', 'Type', 'Status'] },
      mocks: { $t: () => '' }
    })

    expect(wrapper.find('.table-header').text()).toContain('My List (9)')

    // Wait for the component to render after any state changes
    await wrapper.vm.$nextTick()

    // verify table
    expect(wrapper.findComponent(BaseVDataTable).exists()).toBe(true)
    expect(wrapper.findComponent(BaseVDataTable).find(header).exists()).toBe(true)
    expect(wrapper.find('.column-selector').exists()).toBe(true)
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
    expect(columns.at(4).text()).toBe('Open Name Request')

    // second item
    columns = itemRows.at(startCountAt + 1).findAll(itemCell)
    expect(columns.at(0).text()).toBe('BEN NAME REQUEST LIMITED')
    expect(columns.at(1).text()).toBe('NR 4045466')
    expect(columns.at(2).text()).toContain('Name Request')
    expect(columns.at(2).text()).toContain('BC Benefit Company')
    expect(columns.at(3).text()).toBe('Approved')
    expect(columns.at(4).text()).toBe('Open Name Request')

    // third item
    columns = itemRows.at(startCountAt + 2).findAll(itemCell)
    expect(columns.at(0).text()).toBe('BEN NAME REQUEST LIMITED')
    expect(columns.at(1).text()).toBe('NR 4045468')
    expect(columns.at(2).text()).toContain('Name Request')
    expect(columns.at(2).text()).toContain('BC Benefit Company')
    expect(columns.at(3).text()).toBe('Pending Staff Review')
    expect(columns.at(4).text()).toBe('Open Name Request')

    // fourth item
    columns = itemRows.at(startCountAt + 3).findAll(itemCell)
    expect(columns.at(0).text()).toBe('')
    expect(columns.at(1).text()).toBe('')
    expect(columns.at(2).text()).toContain('Registration')
    expect(columns.at(2).text()).toContain('BC Benefit Company')
    expect(columns.at(3).text()).toBe('Draft')
    expect(columns.at(4).text()).toBe('Resume Draft')

    // fifth item
    columns = itemRows.at(startCountAt + 4).findAll(itemCell)
    expect(columns.at(0).text()).toBe('AC SP 2022.MAY.25 15.38 TEST')
    expect(columns.at(1).text()).toBe('NR 2821990')
    expect(columns.at(2).text()).toContain('Name Request')
    expect(columns.at(2).text()).toContain('BC Sole Proprietorship')
    expect(columns.at(3).text()).toBe('Consumed')
    expect(columns.at(4).text()).toBe('Remove From Table')

    // sixth item
    columns = itemRows.at(startCountAt + 5).findAll(itemCell)
    expect(columns.at(0).text()).toBe('Numbered Benefit Company')
    expect(columns.at(1).text()).toBe('Pending')
    expect(columns.at(2).text()).toContain('Incorporation Application')
    expect(columns.at(3).text()).toBe('Draft')
    expect(columns.at(4).text()).toBe('Resume Draft')

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
    expect(columns.at(4).text()).toBe('Manage Business')
  })

  it('Render affiliated entity table with correct actions menu', async () => {
    const businessStore = useBusinessStore()
    businessStore.businesses = moreBusinesses
    sessionStorage[SessionStorageKeys.LaunchDarklyFlags] = JSON.stringify({ 'ia-supported-entities': 'BEN', 'supported-restoration-entities': 'BEN' })
    wrapper = mount(AffiliatedEntityTable, {
      localVue,
      vuetify,
      propsData: { selectedColumns: ['Number', 'Type', 'Status'] },
      mocks: { $t: () => '' }
    })

    expect(wrapper.find('.table-header').text()).toContain('My List (22)')

    // Wait for the component to render after any state changes
    await wrapper.vm.$nextTick()

    // verify table
    expect(wrapper.findComponent(BaseVDataTable).exists()).toBe(true)
    expect(wrapper.findComponent(BaseVDataTable).find(header).exists()).toBe(true)
    expect(wrapper.find('.column-selector').exists()).toBe(true)
    expect(wrapper.find('#affiliated-entity-table').exists()).toBe(true)
    expect(wrapper.find('.v-data-table__wrapper').exists()).toBe(true)
    const titles = wrapper.findComponent(BaseVDataTable).findAll(headerTitles)
    expect(titles.length).toBe(headers.length)
    expect(titles.at(0).text()).toBe('Business Name')
    expect(titles.at(1).text()).toBe('Number')
    expect(titles.at(2).text()).toBe('Type')
    expect(titles.at(3).text()).toBe('Status')
    expect(titles.at(4).text()).toBe('Actions')

    // verify actions menu
    const itemRows = wrapper.findComponent(BaseVDataTable).findAll(itemRow)
    expect(itemRows.length).toBe(moreBusinesses.length)

    for (let i = 0; i < itemRows.length; ++i) {
      const action = itemRows.at(i).findAll(itemCell).at(4)
      expect(action.text()).toBe(actions[i].primary)
      expect(action.find('.external-icon').exists()).toBe(actions[i].external)
      const button = action.find('.more-actions .more-actions-btn')
      await button.trigger('click')

      const secondaryActions = action.findAll('.v-list-item__subtitle')
      for (let j = 0; j < secondaryActions.length; ++j) {
        expect(secondaryActions.at(j).text()).toBe(actions[i].secondary[j])
      }
    }
  })

  it('Tooltips exist in affiliated entity table', async () => {
    wrapper = mount(AffiliatedEntityTable, {
      localVue,
      vuetify,
      propsData: { selectedColumns: ['Number', 'Type', 'Status'] },
      mocks: { $t: () => '' }
    })

    expect(wrapper.findAll('.v-tooltip').exists()).toBeTruthy()
  })

  it('Details for Access Request', async () => {
    wrapper = mount(AffiliatedEntityTable, {
      localVue,
      vuetify,
      propsData: { selectedColumns: ['Number', 'Type', 'Status'] },
      mocks: { $t: () => '' }
    })

    const allWithInvites = businesses.filter(b => b.affiliationInvites)
    expect(wrapper.find('#affiliationInvitesStatus').exists()).toBeTruthy()
    expect(wrapper.findAll('#affiliationInvitesStatus').length).toBe(allWithInvites.length)

    // verify correct invites status is being displayed for each business with invites
    const firstAccSingle = CommonUtils.getElementWithSmallestId<AffiliationInviteInfo>(allWithInvites[0].affiliationInvites)
    const textSingle = `Request for Authorization to manage from: ${firstAccSingle.fromOrg.name}`
    expect(wrapper.findAll('#affiliationInvitesStatus').at(0).text()).toBe(textSingle)

    const firstAccMulti = CommonUtils.getElementWithSmallestId<AffiliationInviteInfo>(allWithInvites[1].affiliationInvites)
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

  it('getRequestForAuthorizationStatusText returns correct text', async () => {
    wrapper = mount(AffiliatedEntityTable, {
      localVue,
      vuetify,
      propsData: { selectedColumns: ['Number', 'Type', 'Status'] },
      mocks: { $t: () => '' }
    })
    const affiliationInvitation = {
      id: 1,
      type: AffiliationInvitationType.REQUEST,
      status: null,
      toOrg: null
    }
    affiliationInvitation.status = AffiliationInvitationStatus.Accepted
    expect(wrapper.vm.getRequestForAuthorizationStatusText([affiliationInvitation]))
      .toBe('Authorization to manage: <strong>Authorized</strong> - you can now manage this business.')
    // Expired will never happen as REQUEST never expire.
    affiliationInvitation.status = AffiliationInvitationStatus.Pending
    expect(wrapper.vm.getRequestForAuthorizationStatusText([affiliationInvitation]))
      .toBe('Authorization to manage: Request sent, pending authorization.')
    affiliationInvitation.status = AffiliationInvitationStatus.Failed
    expect(wrapper.vm.getRequestForAuthorizationStatusText([affiliationInvitation]))
      .toBe('Authorization to manage: <strong>Not Authorized</strong>. Your request to manage this business has been declined.')

    affiliationInvitation.type = AffiliationInvitationType.EMAIL
    affiliationInvitation.status = AffiliationInvitationStatus.Accepted
    expect(wrapper.vm.getRequestForAuthorizationStatusText([affiliationInvitation]))
      .toBe('Authorization to manage: <strong>Authorized</strong> - you can now manage this business.')
    affiliationInvitation.status = AffiliationInvitationStatus.Expired
    expect(wrapper.vm.getRequestForAuthorizationStatusText([affiliationInvitation]))
      .toBe('Authorization to manage: Not authorized. The <strong>confirmation email has expired.</strong>')
    affiliationInvitation.status = AffiliationInvitationStatus.Pending
    expect(wrapper.vm.getRequestForAuthorizationStatusText([affiliationInvitation]))
      .toBe('Authorization to manage: Confirmation Email sent, pending authorization.')
    affiliationInvitation.status = AffiliationInvitationStatus.Failed
    expect(wrapper.vm.getRequestForAuthorizationStatusText([affiliationInvitation]))
      .toBe('Authorization to manage: <strong>Not Authorized</strong>. Your request to manage this business has been declined.')
  })
})
