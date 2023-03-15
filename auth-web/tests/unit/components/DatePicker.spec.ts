import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import { DatePicker } from '@/components'
import Vue from 'vue'
import VueCompositionAPI from '@vue/composition-api'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'

// @ts-ignore
Vue.use(VueCompositionAPI)
Vue.use(Vuetify)

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

const dateSelectors = '.v-date-picker-table--date'
const headers = '.picker-title'
const submitButtons = '.date-selection-btn'

describe('Date Picker tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    const localVue = createLocalVue()
    wrapper = mount(DatePicker, {
      localVue,
      vuetify,
      propsData: {
        setEndDate: null,
        setStartDate: null
      }
    })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders and displays the date picker', async () => {
    expect(wrapper.findComponent(DatePicker).exists()).toBe(true)
    expect(wrapper.findAll(headers).length).toBe(2)
    expect(wrapper.findAll(headers).at(0).text()).toBe('Select Start Date:')
    expect(wrapper.findAll(headers).at(1).text()).toBe('Select End Date:')
    expect(wrapper.findAll(dateSelectors).length).toBe(2)
    expect(wrapper.findAll(submitButtons).length).toBe(2)
    expect(wrapper.findAll(submitButtons).at(0).text()).toBe('OK')
    expect(wrapper.findAll(submitButtons).at(1).text()).toBe('Cancel')
    expect(wrapper.vm.datePickerErr).toBe(false)
  })

  it('Validates and submits the date selections', async () => {
    // verify setup
    expect(wrapper.findAll(dateSelectors).length).toBe(2)
    expect(wrapper.findAll(submitButtons).length).toBe(2)
    expect(wrapper.findAll(submitButtons).at(0).text()).toBe('OK')
    expect(wrapper.findAll(submitButtons).at(1).text()).toBe('Cancel')
    expect(wrapper.vm.datePickerErr).toBe(false)
    // click okay + test validation
    wrapper.findAll(submitButtons).at(0).trigger('click')
    await flushPromises()
    expect(wrapper.vm.datePickerErr).toBe(true)
    expect(wrapper.emitted('submit')).toBeUndefined()
    // click cancel + test validation reset / emit nulls
    wrapper.findAll(submitButtons).at(1).trigger('click')
    await flushPromises()
    expect(wrapper.vm.datePickerErr).toBe(false)
    expect(wrapper.emitted('submit').length).toBe(1)
    expect(wrapper.emitted('submit')[0]).toEqual([{ endDate: null, startDate: null }])
    // set start date only + test validation
    const startDate = '2021-10-22'
    wrapper.vm.startDate = startDate
    await flushPromises()
    expect(wrapper.vm.startDate).toBe(startDate)
    // should still trigger validation err
    wrapper.findAll(submitButtons).at(0).trigger('click')
    await flushPromises()
    expect(wrapper.vm.datePickerErr).toBe(true)
    // last event will be the same as before
    expect(wrapper.emitted('submit').length).toBe(1)
    expect(wrapper.emitted('submit')[0]).toEqual([{ endDate: null, startDate: null }])
    // select end date and submit should emit values
    const endDate = '2021-10-23'
    wrapper.vm.endDate = endDate
    await flushPromises()
    expect(wrapper.vm.endDate).toBe(endDate)
    wrapper.findAll(submitButtons).at(0).trigger('click')
    await flushPromises()
    expect(wrapper.vm.datePickerErr).toBe(false)
    expect(wrapper.emitted('submit').length).toBe(2)
    expect(wrapper.emitted('submit')[1]).toEqual([{ startDate: startDate, endDate: endDate }])
  })
})
