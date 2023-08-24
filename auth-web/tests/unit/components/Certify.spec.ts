import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import Certify from '@/components/auth/manage-business/manage-business-dialog/Certify.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

describe('Add Business Form', () => {
  let wrapper: Wrapper<any>

  beforeAll(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({ strict: false })

    wrapper = mount(Certify, {
      store,
      localVue,
      vuetify,
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
