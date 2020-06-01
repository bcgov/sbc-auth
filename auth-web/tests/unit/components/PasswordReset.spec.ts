import { createLocalVue, mount } from '@vue/test-utils'
import ModalDialog from '@/components/auth/ModalDialog.vue'
import PasswordRequirementAlert from '@/components/auth/common/PasswordRequirementAlert.vue'
import PasswordReset from '@/components/auth/PasswordReset.vue'
import { User } from '@/models/user'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import flushPromises from 'flush-promises'

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

    wrapperFactory = (propsData) => {
      return mount(PasswordReset, {
        localVue,
        store,
        vuetify,
        stubs: { }
      })
    }

    wrapper = wrapperFactory({ PasswordReset: {} })
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('renders the components properly', () => {
    expect(wrapper.find(PasswordReset).exists()).toBe(true)
  })

  it('renders the components properly', () => {
    expect(wrapper.find(PasswordReset).exists()).toBe(true)
  })

  it('doesnt show modal before open is called', async () => {
    const dialogele = wrapper.find('.v-dialog')
    expect(wrapper.find(PasswordRequirementAlert).exists()).toBe(false)
    expect(dialogele.isVisible()).toBe(false)
  })

  it('shows modal when open is called', async () => {
    const user: User = { firstname: '', lastname: '', username: '' }
    await wrapper.vm.openDialog(user)
    const dialogele = wrapper.find('.v-dialog')
    expect(dialogele.classes('v-dialog--active')).toBe(true)
    expect(dialogele.isVisible()).toBe(true)
    expect(wrapper.find(PasswordRequirementAlert).exists()).toBe(true)
  })
  it('click the reset password', async () => {
    const user: User = { firstname: '', lastname: '', username: '' }
    await wrapper.vm.openDialog(user)
    const dialogele = wrapper.find('.v-dialog')
    expect(dialogele.classes('v-dialog--active')).toBe(true)
    expect(dialogele.isVisible()).toBe(true)
    expect(wrapper.find(PasswordRequirementAlert).exists()).toBe(true)
  })
})
