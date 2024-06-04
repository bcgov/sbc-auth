import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import { useStaffStore, useUserStore } from '@/stores'
import CardHeader from '@/components/CardHeader.vue'
import DissolutionSchedule from '@/components/auth/staff/DissolutionSchedule.vue'
import InvoluntaryDissolution from '@/views/auth/staff/InvoluntaryDissolution.vue'
import { Role } from '@/util/constants'
import StaffService from '../../../src/services/staff.services'
import Vue from 'vue'
import Vuetify from 'vuetify'

const vuetify = new Vuetify({})

describe('StaffDashboardView tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    const localVue = createLocalVue()

    vi.spyOn((StaffService as any), 'getDissolutionStatistics').mockImplementation(() => ({}))

    const staffStore = useStaffStore()
    staffStore.dissolutionStatistics = {
      data: { 'eligibleCount': 300 }
    }

    const userStore = useUserStore()
    userStore.currentUser = {
      roles: [Role.Staff]
    } as any

    wrapper = mount(InvoluntaryDissolution, {
      localVue,
      vuetify
    })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders components properly', () => {
    expect(wrapper.findComponent(CardHeader).exists()).toBe(true)
    expect(wrapper.findComponent(DissolutionSchedule).exists()).toBe(true)
    expect(wrapper.findComponent(InvoluntaryDissolution).exists()).toBe(true)
    expect(wrapper.find('#company-summary-vcard').exists()).toBe(true)
    expect(wrapper.find('.loading-container').exists()).toBe(true)
    expect(wrapper.find('.view-header').exists()).toBe(true)
  })

  it('renders child components with correct information', async () => {
    await Vue.nextTick()
    expect(wrapper.find('h1').text()).toBe('Staff Involuntary Dissolution Batch')
    expect(wrapper.find('h2').text()).toBe('Automated Dissolution')
    expect(wrapper.findAll('p').at(0).text()).toBe('B.C. Business Ready for D1 Dissolution: 300')
    expect(wrapper.findAll('p').at(1).text()).toContain('You can set up a schedule to automate the involuntary dissolution process.')
  })
})
