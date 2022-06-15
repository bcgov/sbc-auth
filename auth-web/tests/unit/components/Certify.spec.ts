import { Wrapper, mount } from '@vue/test-utils'
import Certify from '@/components/auth/manage-business/Certify.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

describe('Add Business Form', () => {
  let wrapper: Wrapper<any>

  beforeAll(() => {
    wrapper = mount(Certify, {
      vuetify,
      propsData: {
        legalName: 'Legal Name',
        entity: 'entity',
        clause: 'Lorem ipsum dolor sit amet.'
      }
    })
  })

  afterAll(() => {
    wrapper.destroy()
  })

  it('renders the component properly', () => {
    // verify component
    expect(wrapper.attributes('id')).toBe('certify')
    expect(wrapper.find('#certify').isVisible()).toBe(true)

    // verify checkbox
    expect(wrapper.find('.certify-checkbox label').text()).toContain('Legal Name')
    expect(wrapper.find('.certify-checkbox label').text()).toContain('certifies that')
    expect(wrapper.find('.certify-checkbox label').text()).toContain('of the entity')
    expect(wrapper.find('.certify-clause').text()).toBe('Lorem ipsum dolor sit amet.')
  })
})
