import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import Certify from '@/components/auth/manage-business/Certify.vue'
import Vuetify from 'vuetify'

describe('Add Business Form', () => {
  let wrapper: Wrapper<any>

  beforeAll(() => {
    const localVue = createLocalVue()

    wrapper = mount(Certify, {
      localVue,
      vuetify: new Vuetify({}),
      propsData: {
        entity: 'entity',
        certifiedBy: 'Woodie, Nadia'
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

    // verify checkbox label text
    const text = wrapper.find('.certify-checkbox label').text()
    expect(text).toContain('Woodie, Nadia')
    expect(text).toContain('certifies that')
    expect(text).toContain('they have relevant')
    expect(text).toContain('on behalf of this')
  })
})
