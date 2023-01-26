
import { Wrapper, createLocalVue, mount, shallowMount } from '@vue/test-utils'
import { DateFilterCodes } from '@/util/constants'
import DateRangeFilter from '@/components/auth/common/DateRangeFilter.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import moment from 'moment'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('DateRangeFilter.vue', () => {
  let wrapper: any

  const app = document.createElement('div')
  app.setAttribute('data-app', 'true')
  document.body.append(app)

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(Vuetify)

    const vuetify = new Vuetify({})

    wrapper = mount(DateRangeFilter, {
      localVue,
      vuetify,
      propsData: {
        dateFilterProp: {}
      },
      attachToDocument: true
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('is Date Range button exists', () => {
    expect(wrapper.find('.date-range-btn')).toBeTruthy()
    expect(wrapper.find('.date-range-btn').text()).toBe('Date Range')
  })

  it('is Date Range button click opens the date picker modal', () => {
    expect(wrapper.vm.$data.showDateFilter).toBe(false)
    wrapper.find('.date-range-btn').trigger('click')
    expect(wrapper.vm.$data.showDateFilter).toBe(true)
    expect(wrapper.find('.date-range-container')).toBeTruthy()
  })

  it('is date picker modal has buttons', () => {
    wrapper.find('.date-range-btn').trigger('click')
    expect(wrapper.find('.apply-btn')).toBeTruthy()
    expect(wrapper.find('.cancel-btn')).toBeTruthy()
  })

  it('is formatting datepicker date correctly', () => {
    const currentDate = moment().format('YYYY-MM-DD')
    expect(wrapper.vm.formatDatePickerDate(moment())).toEqual(currentDate)
  })

  it('is formatting date filter correctly', () => {
    expect(wrapper.vm.formatDateFilter('2020-09-14')).toEqual('2020-09-14')
  })

  it('[neg] is formatting date filter correctly', () => {
    expect(wrapper.vm.formatDateFilter()).toBeNull()
  })

  it('is apply filter button valid if both dates are selected', () => {
    wrapper.vm.$data.dateRangeSelected = ['2020-08-01']
    expect(wrapper.vm.isApplyFilterBtnValid).toBeFalsy()
    wrapper.vm.$data.dateRangeSelected = ['2020-08-01', '2020-08-31']
    expect(wrapper.vm.isApplyFilterBtnValid).toBe(true)
  })

  it('is dateClick function automatically switch to custom date', () => {
    wrapper.vm.dateClick('2020-09-09')
    expect(wrapper.vm.dateFilterSelected?.code).toEqual(DateFilterCodes.CUSTOMRANGE)
  })

  // it('is clicking date in the date picker automatically switch to custom range', async () => {
  //   wrapper.find('.date-range-btn').trigger('click')
  //   await wrapper.vm.$nextTick()
  //   wrapper.findAll('.v-date-picker-table table tbody td').at(5).find('.v-btn').trigger('click')
  //   await wrapper.vm.$nextTick()
  //   expect(wrapper.vm.dateFilterSelected?.code).toEqual(DateFilterCodes.CUSTOMRANGE)
  // })

  it('is date filter change should show the correct range for last week', () => {
    const start = moment().subtract(1, 'weeks').startOf('isoWeek').format('YYYY-MM-DD')
    const end = moment().subtract(1, 'weeks').endOf('isoWeek').format('YYYY-MM-DD')
    const indexOfRange = wrapper.vm.$data.dateFilterRanges.findIndex((filterRange) => (filterRange.code === DateFilterCodes.LASTWEEK))
    wrapper.vm.dateFilterChange(indexOfRange)
    expect(wrapper.vm.dateFilterSelected?.code).toEqual(DateFilterCodes.LASTWEEK)
    expect(wrapper.vm.dateRangeSelected).toEqual([start, end])
    expect(wrapper.vm.dateRangeSelected).not.toEqual([start, start])
  })

  it('is date filter change should show the correct range today', () => {
    const start = moment().format('YYYY-MM-DD')
    const indexOfRange = wrapper.vm.$data.dateFilterRanges.findIndex((filterRange) => (filterRange.code === DateFilterCodes.TODAY))
    wrapper.vm.dateFilterChange(indexOfRange)
    expect(wrapper.vm.dateFilterSelected?.code).toEqual(DateFilterCodes.TODAY)
    expect(wrapper.vm.dateRangeSelected).toEqual([start, start])
  })

  it('is date filter should show the correct label of selected range', () => {
    const start = moment().format('YYYY-MM-DD')
    wrapper.vm.$data.dateFilterSelected = wrapper.vm.$data.dateFilterRanges.find((filterRange) => (filterRange.code === DateFilterCodes.TODAY))
    wrapper.vm.$data.dateRangeSelected = ['2020-09-19', '2020-09-19']
    expect(wrapper.vm.showDateRangeSelected).toBe('<strong>Today:</strong> 09-19-2020')
  })

  it('initialize before opening date filter model ', () => {
    expect(wrapper.vm.showDateFilter).toBeFalsy()
    wrapper.vm.openDateFilter()
    expect(wrapper.vm.showDateFilter).toBeTruthy()
    expect(wrapper.vm.dateFilterSelectedIndex).toBeNull()
  })

  it('initialize filter model ', () => {
    wrapper.vm.initDatePicker()
    expect(wrapper.vm.dateFilterSelectedIndex).toBeNull()
    expect(wrapper.vm.dateRangeSelected).toEqual([])
    expect(wrapper.vm.dateFilterSelected).toEqual({})
  })

  it('emits the values ', async () => {
    wrapper.vm.$emit('emit-date-filter')
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('emit-date-filter')).toBeTruthy()
  })

  it('renders correct number of date ranges ', async () => {
    wrapper.find('.date-range-btn').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.findAll('.date-range-options .v-list-item-group .v-list-item').length).toBe(Object.keys(DateFilterCodes).length)
  })

  it('is date filter emiting correct values', async () => {
    wrapper.find('.date-range-btn').trigger('click')
    await wrapper.vm.$nextTick()
    const today = moment().format('YYYY-MM-DD')
    const indexOfRange = wrapper.vm.$data.dateFilterRanges.findIndex((filterRange) => (filterRange.code === DateFilterCodes.TODAY))
    wrapper.vm.dateFilterChange(indexOfRange)
    expect(wrapper.vm.dateRangeSelected).toEqual([today, today])
    wrapper.vm.emitDateFilter()
    await wrapper.vm.$nextTick()
    const emitVal = {
      startDate: wrapper.vm.formatDateFilter(wrapper.vm.dateRangeSelected[0]),
      endDate: wrapper.vm.formatDateFilter(wrapper.vm.dateRangeSelected[1])
    }
    expect(wrapper.emitted('emit-date-filter')[0][0]).toEqual(emitVal)
  })
})
