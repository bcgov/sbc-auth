import { createLocalVue, mount } from '@vue/test-utils'
import StaffContinuationApplicationTable from '@/components/auth/staff/continuation-application/StaffContinuationApplicationTable.vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})
const router = new VueRouter()

describe('StaffContinuationApplicationTable.vue', () => {
  let wrapper: any
  let store: any
  const localVue = createLocalVue()

  beforeEach(() => {
    wrapper = mount(StaffContinuationApplicationTable, {
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
          status: 'Accepted',
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
})
