import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import Certify from '@/components/auth/manage-business/Certify.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import UserModule from '@/store/modules/user'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

describe('Add Business Form', () => {
  let wrapper: Wrapper<any>
  let userModule: any

  userModule = {
    namespaced: true,
    state: {
      currentUser: {
        firstName: 'Nadia',
        lastName: 'Woodie'
      }
    },
    actions: UserModule.actions,
    mutations: UserModule.mutations,
    getters: UserModule.getters
  }

  beforeAll(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({
      strict: false,
      modules: {
        user: userModule
      }
    })

    wrapper = mount(Certify, {
      store,
      localVue,
      vuetify,
      propsData: {
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
    expect(wrapper.find('.certify-checkbox label').text()).toContain('Woodie, Nadia')
    expect(wrapper.find('.certify-checkbox label').text()).toContain('certifies that')
    expect(wrapper.find('.certify-checkbox label').text()).toContain('of the entity')
    expect(wrapper.find('.certify-clause').text()).toBe('Lorem ipsum dolor sit amet.')
  })
})
