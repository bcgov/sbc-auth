import { createLocalVue, mount } from '@vue/test-utils'
import { SearchFilterCodes } from '@/util/constants'
import SearchFilterInput from '@/components/auth/common/SearchFilterInput.vue'
import Vuetify from 'vuetify'

describe('SearchFilterInput.vue', () => {
  let wrapper: any

  const filterParams = [
    {
      id: SearchFilterCodes.USERNAME,
      placeholder: 'User Name',
      labelKey: 'Name',
      appliedFilterValue: '',
      filterInput: ''
    },
    {
      id: SearchFilterCodes.FOLIONUMBER,
      placeholder: 'Folio Number',
      labelKey: 'Folio',
      appliedFilterValue: '',
      filterInput: ''
    }
  ]
  const filteredRecordsCount = 0

  const app = document.createElement('div')
  app.setAttribute('data-app', 'true')
  document.body.append(app)

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuetify)

    const vuetify = new Vuetify({})

    wrapper = mount(SearchFilterInput, {
      localVue,
      vuetify,
      propsData: {
        filterParams: filterParams,
        filteredRecordsCount: filteredRecordsCount
      },
      attachToDocument: true
    })

    vi.resetModules()
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('has search fields and apply button', () => {
    expect(wrapper.find('.filter-input')).toBeTruthy()
    expect(wrapper.find('.apply-filter-btn')).toBeTruthy()
  })

  it('confirm search field count as per the prop given', () => {
    const filterCount = wrapper.vm.$props.filterParams.length
    const renderedInputs = wrapper.findAll('.filter-input')
    expect(renderedInputs?.length).toEqual(filterCount)
  })

  it('renders the input fields with correct labels', () => {
    const renderedInputs = wrapper.vm.$el.querySelectorAll('.filter-input')
    expect(renderedInputs[0].getElementsByTagName('label')[0].innerHTML === filterParams[0].placeholder)
    expect(renderedInputs[1].getElementsByTagName('label')[0].innerHTML === filterParams[1].placeholder)
  })

  it('renders the input fields with correct values and apply filter disabled', () => {
    const renderedInputs = wrapper.vm.$el.querySelectorAll('.filter-input')
    expect(renderedInputs[0].getElementsByTagName('input')[0].value).toBe('')
    expect(renderedInputs[1].getElementsByTagName('input')[0].value).toBe('')
    expect(wrapper.find('.apply-filter-btn').is('[disabled]')).toBe(true)
  })

  it('input username in the search field', async () => {
    const userNameSearchField = wrapper.findAll('.filter-input').at(0)
    userNameSearchField.element.value = 'Jon Snow'
    userNameSearchField.trigger('input')
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.apply-filter-btn').is('[disabled]')).toBe(true)
  })
})
