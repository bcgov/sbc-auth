import { Wrapper, mount } from '@vue/test-utils'
import { SubProductConfigIF } from '@/models/SubProductConfigIF'
import SubProductSelector from '@/components/auth/common/SubProductSelector.vue'
import Vue from 'vue'
import VueCompositionAPI from '@vue/composition-api'
import Vuetify from 'vuetify'

// @ts-ignore
Vue.use(VueCompositionAPI)
Vue.use(Vuetify)
const vuetify = new Vuetify({})

describe('SubProductSelector', () => {
  it('renders the component', () => {
    const wrapper: Wrapper<any> = mount(SubProductSelector, {
      vuetify,
      propsData: {
        subProductConfig: []
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('renders the correct amount of sub-products', async () => {
    const subProductConfig: Array<SubProductConfigIF> = [
      {
        type: 'subProduct1',
        label: 'Sub Product 1',
        productBullets: ['Bullet 1', 'Bullet 2'],
        note: 'This is a note'
      },
      {
        type: 'subProduct2',
        label: 'Sub Product 2',
        productBullets: ['Bullet 1', 'Bullet 2'],
        note: ''
      }
    ]

    const wrapper: Wrapper<any> = mount(SubProductSelector, {
      vuetify,
      propsData: {
        subProductConfig
      }
    })

    const radioGroup = wrapper.find('.sub-product-radio-group')
    expect(radioGroup.exists()).toBe(true)

    const subProductRows = wrapper.findAll('.sub-product-radio-wrapper')
    expect(subProductRows.length).toBe(2)
  })

  it('renders sub-product bullets correctly', async () => {
    const subProductConfig: Array<SubProductConfigIF> = [
      {
        type: 'subProduct1',
        label: 'Sub Product 1',
        productBullets: ['Bullet 1', 'Bullet 2'],
        note: ''
      }
    ]

    const wrapper: Wrapper<any> = mount(SubProductSelector, {
      vuetify,
      propsData: {
        subProductConfig
      }
    })

    const bullets = wrapper.findAll('.bullet')
    expect(bullets.length).toBe(2)
    expect(bullets.at(0).text()).toBe('Bullet 1')
    expect(bullets.at(1).text()).toBe('Bullet 2')
  })

  it('renders sub-product note correctly', async () => {
    const subProductConfig: Array<SubProductConfigIF> = [
      {
        type: 'subProduct1',
        label: 'Sub Product 1',
        productBullets: [],
        note: '<strong>Note:</strong> This is a note'
      }
    ]

    const wrapper: Wrapper<any> = mount(SubProductSelector, {
      vuetify,
      propsData: {
        subProductConfig
      }
    })

    const note = wrapper.find('.sub-product-note')
    expect(note.exists()).toBe(true)
    expect(note.text()).toContain('Note:')
    expect(note.html()).toContain('<strong>Note:</strong> This is a note')
  })
})
