import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import { BaseTableHeaderI } from '@/components/datatable/interfaces'
import { BaseVDataTable } from '@/components/datatable'
import { DEFAULT_DATA_OPTIONS } from '@/components/datatable/resources'
import Vue from 'vue'
import VueCompositionAPI from '@vue/composition-api'
import Vuetify from 'vuetify'

// @ts-ignore
Vue.use(VueCompositionAPI)
Vue.use(Vuetify)

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

// selectors
const header = '.base-table__header'
const headerTitles = `${header}__title`
const headerFilters = `${header}__filter`
const headerFilterSelects = `${headerFilters}__select`
const headerFilterTextbox = `${headerFilters}__textbox`
const itemRow = '.base-table__item-row'
const itemCell = '.base-table__item-cell'

// test setup values
const items = [{ id: '0', desc1: 'lala 1', desc2: 'lala 2' }, { id: '1', desc1: 'weewaa 1', desc2: 'weewaa 1' }]
const headersBasic: BaseTableHeaderI[] = [
  { col: 'id', hasFilter: false, value: 'ID Header' },
  { col: 'desc1', hasFilter: false, itemFn: (val: any) => `${val.desc1}111`, value: 'Title Desc 1' }
]
const headersUpdated: BaseTableHeaderI[] = [
  { col: 'id', hasFilter: false, value: 'ID Header' },
  { col: 'desc1', hasFilter: false, itemFn: (val: any) => `${val.desc1}111`, value: 'Title Desc 1' },
  { col: 'desc2', hasFilter: false, itemFn: (val: any) => `${val.desc2}222`, value: 'Desc 2' }
]
const headersWithFilters: BaseTableHeaderI[] = [
  {
    col: 'id',
    customFilter: {
      clearable: false,
      filterApiFn: jest.fn(),
      items: [{ text: 'one', value: 1 }, { text: 'two', value: 2 }],
      type: 'select',
      value: ''
    },
    hasFilter: true,
    value: 'ID Header'
  },
  {
    col: 'desc1',
    customFilter: {
      clearable: false,
      filterApiFn: jest.fn(),
      type: 'text',
      value: ''
    },
    hasFilter: true,
    value: 'Title Desc 1'
  }
]

const validateHeaders = async (wrapper: Wrapper<any>) => {
  // validate header titles / filtersof the table
  const headers = wrapper.vm.headers as BaseTableHeaderI[]
  expect(wrapper.find(header).exists()).toBe(true)
  const titles = wrapper.findAll(headerTitles)
  const filters = wrapper.findAll(headerFilters)
  expect(titles.length).toBe(headers.length)
  expect(filters.length).toBe(headers.length)
  for (let i = 0; i < headers.length; i++) {
    expect(titles.at(i).text()).toBe(headers[i].value)
    if (headers[i].hasFilter) {
      let filter
      if (headers[i].customFilter.type === 'select') filter = filters.at(i).findAll(headerFilterSelects)
      else filter = filters.at(i).findAll(headerFilterTextbox)
      expect(filter.length).toBe(1)
    }
  }
}

const validateItems = async (wrapper: Wrapper<any>) => {
  // validate item values
  const headers = wrapper.vm.headers as BaseTableHeaderI[]
  const sortedItems = wrapper.vm.sortedItems as object[]
  const itemRows = wrapper.findAll(itemRow)
  expect(itemRows.length).toBe(sortedItems.length)
  for (let i = 0; i < itemRows.length; i++) {
    const cells = itemRows.at(i).findAll(itemCell)
    expect(cells.length).toBe(headers.length)
    for (let k = 0; k < cells.length; k++) {
      if (headers[k].itemFn) {
        expect(cells.at(k).text()).toEqual(headers[k].itemFn(sortedItems[i]))
      } else {
        expect(cells.at(k).text()).toEqual(sortedItems[i][headers[k].col])
      }
    }
  }
}

describe('Base datatable tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    const localVue = createLocalVue()
    wrapper = mount(BaseVDataTable, {
      localVue,
      vuetify,
      propsData: {
        itemKey: 'id',
        setItems: items,
        setHeaders: headersBasic,
        totalItems: items.length,
        height: '100%'
      }
    })
  })

  afterEach(async () => {
    wrapper.destroy()
  })

  it('renders and displays the base datatable', async () => {
    expect(wrapper.findComponent(BaseVDataTable).exists()).toBe(true)
    // verify setup
    expect(wrapper.vm.setHeaders).toEqual(headersBasic)
    expect(wrapper.vm.setItems).toEqual(items)
    expect(wrapper.vm.headers).toEqual(headersBasic)
    expect(wrapper.vm.sortedItems).toEqual(items)
    expect(wrapper.vm.clearFiltersTrigger).toEqual(1)
    expect(wrapper.vm.totalItems).toEqual(items.length)
    expect(wrapper.vm.tableDataOptions).toEqual(DEFAULT_DATA_OPTIONS)
    expect(wrapper.vm.clearFiltersTrigger).toEqual(1)
    // check it out
    await validateHeaders(wrapper)
    await validateItems(wrapper)
  })

  it('dynamically updates headers and items', async () => {
    const itemsUpdated = [...items]
    itemsUpdated.push({ id: '3', desc1: 'updated 1', desc2: 'updated 2' })
    // update props
    wrapper.setProps({ setHeaders: headersUpdated, setItems: itemsUpdated })
    await Vue.nextTick()
    // verify changed
    expect(wrapper.vm.headers).toEqual(headersUpdated)
    expect(wrapper.vm.sortedItems).toEqual(itemsUpdated)
    // check it out
    await validateHeaders(wrapper)
    await validateItems(wrapper)
  })

  it('supports headers with filters', async () => {
    // update header to one with filters set
    wrapper.setProps({ setHeaders: headersWithFilters })
    await Vue.nextTick()
    expect(wrapper.vm.setHeaders).toEqual(headersWithFilters)
    // verify changed
    expect(wrapper.vm.headers).toEqual(headersWithFilters)
    // check it out
    await validateHeaders(wrapper)
    await validateItems(wrapper)
  })
})
