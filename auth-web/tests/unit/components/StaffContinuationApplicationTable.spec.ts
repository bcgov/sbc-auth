import { createLocalVue, mount } from '@vue/test-utils'
import ContinuationApplicationTable from '@/components/auth/staff/continuation-application/ContinuationApplicationTable.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})
const router = new VueRouter()

describe('StaffContinuationApplicationTable.vue', () => {
  let wrapper: any
  let store: any
  const localVue = createLocalVue()

  beforeEach(() => {
    wrapper = mount(ContinuationApplicationTable, {
      store,
      vuetify,
      localVue,
      router,

      mocks: {
        $t: (mock) => mock
      }
    })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('Should have data table', () => {
    expect(wrapper.find('.v-data-table')).toBeTruthy()
  })

  it('Should render correct button labels', async () => {
    wrapper.setData({
      reviews: [
        {
          reviewId: '123',
          status: 'Awaiting Review',
          date: '2024-05-01',
          nrNumber: 'NR 1234567',
          businessIdentifier: 'LN987234',
          completingParty: 'James Smith'
        },
        {
          reviewId: '124',
          status: 'Approved',
          date: '2024-05-01',
          nrNumber: 'NR 1234568',
          businessIdentifier: 'LN987235',
          completingParty: 'John Doe'
        }
      ]
    })

    await wrapper.vm.$nextTick()

    const reviewButton = wrapper.find(`[data-test="view-continuation-button-123"]`)
    const viewButton = wrapper.find(`[data-test="view-continuation-button-124"]`)

    expect(reviewButton.text()).toBe('Review')
    expect(viewButton.text()).toBe('View')
  })

  it('should fetch and render data correctly', async () => {
    wrapper.setData({
      reviews: [
        {
          reviewId: '123',
          status: 'Awaiting Review',
          date: '2024-05-01',
          nrNumber: 'NR 1234567',
          businessIdentifier: 'LN987234',
          completingParty: 'James Smith'
        },
        {
          reviewId: '124',
          status: 'Approved',
          date: '2024-05-02',
          nrNumber: 'NR 1234568',
          businessIdentifier: 'LN987235',
          completingParty: 'John Doe'
        }
      ]
    })

    await wrapper.vm.$nextTick()

    const rows = wrapper.findAll('tbody tr')
    expect(rows.length).toBe(2)

    const firstRowColumns = rows.at(0).findAll('td')
    expect(firstRowColumns.at(0).text()).toBe('2024-05-01')
    expect(firstRowColumns.at(1).text()).toBe('NR 1234567')
    expect(firstRowColumns.at(2).text()).toBe('LN987234')
    expect(firstRowColumns.at(3).text()).toBe('James Smith')
    expect(firstRowColumns.at(4).text()).toBe('Awaiting Review')

    const secondRowColumns = rows.at(1).findAll('td')
    expect(secondRowColumns.at(0).text()).toBe('2024-05-02')
    expect(secondRowColumns.at(1).text()).toBe('NR 1234568')
    expect(secondRowColumns.at(2).text()).toBe('LN987235')
    expect(secondRowColumns.at(3).text()).toBe('John Doe')
    expect(secondRowColumns.at(4).text()).toBe('Approved')
  })
})
