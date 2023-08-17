import { createLocalVue, mount } from '@vue/test-utils'
import PasswordReset from '@/components/auth/account-settings/team-management/PasswordReset.vue'
import { User } from '@/models/user'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('PasswordReset.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({})
    const user:User = { firstname: '', lastname: '', 'username': 'testuser' }
    wrapperFactory = () => {
      return mount(PasswordReset, {
        localVue,
        store,
        vuetify,
        stubs: { },
        propsData: { user: user }
      })
    }

    wrapper = wrapperFactory({ PasswordReset: {} })
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the components properly', () => {
    expect(wrapper.findComponent(PasswordReset).exists()).toBe(true)
  })

  it('renders the components properly', async () => {
    expect(wrapper.findComponent(PasswordReset).exists()).toBe(true)
    const authenticatedBtns = wrapper.vm.$el.querySelectorAll('.v-btn')
    const titleText = wrapper.vm.$el.querySelectorAll('p')
    expect(titleText.length).toStrictEqual(1)
    expect(authenticatedBtns.length).toStrictEqual(2)
  })
})
