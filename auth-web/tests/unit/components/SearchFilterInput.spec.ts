import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import { toBeDisabled, toHaveAttribute, toHaveValue } from '@testing-library/jest-dom/matchers'
import SearchFilterInput from '@/components/auth/common/SearchFilterInput.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

expect.extend({ toHaveAttribute, toHaveValue, toBeDisabled })

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('SearchFilterInput.vue', () => {
  let wrapper: any
  const config = {
    'VUE_APP_ROOT_API': 'https://localhost:8080/api/v1/11'
  }

  const filterParams = [
    {
      id: 'username',
      placeholder: 'User Name',
      labelKey: 'Name',
      appliedFilterValue: '',
      filterInput: ''
    },
    {
      id: 'folio',
      placeholder: 'Folio Number',
      labelKey: 'Folio',
      appliedFilterValue: '',
      filterInput: ''
    }
  ]
  let filteredRecordsCount = 0

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const vuetify = new Vuetify({})

    wrapper = mount(SearchFilterInput, {
      localVue,
      vuetify,
      propsData: {
        filterParams: filterParams,
        filteredRecordsCount: filteredRecordsCount
      },
      sync: false
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('has search fields and apply button', () => {
    expect(wrapper.find('.filter-input')).toBeTruthy()
    expect(wrapper.find('.apply-filter-btn')).toBeTruthy()
  })

  it('confirm search field count as per the prop given', () => {
    const filterCount = wrapper.vm.$props.filterParams.length
    const renderedInputs = wrapper.vm.$el.querySelectorAll('.filter-input')
    expect(renderedInputs?.length).toEqual(filterCount)
  })

  it('renders the input fields with correct labels', () => {
    const renderedInputs = wrapper.vm.$el.querySelectorAll('.filter-input')
    expect(renderedInputs[0].getElementsByTagName('input')[0].getAttribute('placeholder')).toBe(filterParams[0].placeholder)
    expect(renderedInputs[1].getElementsByTagName('input')[0].getAttribute('placeholder')).toBe(filterParams[1].placeholder)
  })

  it('renders the input fields with correct values and apply filter disabled', () => {
    const renderedInputs = wrapper.vm.$el.querySelectorAll('.filter-input')
    expect(renderedInputs[0].getElementsByTagName('input')[0]).toHaveValue('')
    expect(renderedInputs[1].getElementsByTagName('input')[0]).toHaveValue('')
    expect(wrapper.vm.$el.querySelector('.apply-filter-btn')).toBeDisabled()
  })

  it('input username in the search field', async () => {
    const userNameSearchField = wrapper.findAll('.filter-input').at(0)
    userNameSearchField.element.value = 'Jon Snow'
    userNameSearchField.trigger('input')
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.$el.querySelector('.apply-filter-btn')).toBeDisabled()
  })
})
