import { createLocalVue, shallowMount } from '@vue/test-utils'
import DashboardHelp from '@/components/auth/manage-business/DashboardHelp.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const localVue = createLocalVue()
localVue.use(VueRouter)

describe('Dashboard Help component', () => {
  let wrapper: any

  beforeAll(() => {
    localVue.use(Vuex)
    const store = new Vuex.Store({})
    wrapper = shallowMount(DashboardHelp, { vuetify, localVue, store })
  })

  it('DashboardHelp is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('html renders correctly for DashboardHelp component', async () => {
    expect(wrapper.find('#dashboard-help').exists()).toBe(true)
    expect(wrapper.find('#btn-buissness-help').exists()).toBe(true)
  })

  afterAll(() => {
    wrapper.destroy()
  })
})
