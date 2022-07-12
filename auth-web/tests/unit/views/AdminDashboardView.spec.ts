import { Wrapper, mount, shallowMount } from '@vue/test-utils'
import AdminDashboardView from '@/views/auth/staff/AdminDashboardView.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

describe('Search Business Form: Initial', () => {
  const wrapper: Wrapper<any> = mount(AdminDashboardView, {
    vuetify,
    propsData: {}
  })

  it('renders the component properly', () => {
    // verify component
    expect(wrapper.find('#txtBusinessNumber').isVisible()).toBe(true)
    expect(wrapper.find('.search-btn').attributes('disabled')).toBe('disabled')
  })
})

describe('Search Business Form: Result', () => {
  const wrapper: Wrapper<any> = shallowMount(AdminDashboardView, {
    vuetify,
    propsData: {}
  })

  it('renders the component properly', () => {
    // verify component
    wrapper.setData({ businessDetails: {
      legalName: 'Business Name',
      identifier: 'FM1234567',
      taxId: '123456789BC0001' }
    })
    expect(wrapper.find('.business-details').isVisible()).toBe(true)
  })
})
