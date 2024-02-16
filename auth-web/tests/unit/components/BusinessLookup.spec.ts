import BusinessLookup from '@/components/auth/manage-business/BusinessLookup.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import { mount } from '@vue/test-utils'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

describe('Business Lookup component', () => {
  let wrapper: any

  beforeEach(() => {
    wrapper = mount(BusinessLookup, { vuetify })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the component properly', () => {
    expect(wrapper.find('#business-lookup').exists()).toBe(true)
    expect(wrapper.find('.v-input__slot').text()).toBe('My business name, incorporation, or registration number')
    expect(wrapper.find('.v-text-field__details').text()).toContain('For example:')
  })
})
