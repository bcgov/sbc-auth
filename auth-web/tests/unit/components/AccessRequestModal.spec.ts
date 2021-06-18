
import { createLocalVue, mount } from '@vue/test-utils'

import AccessRequestModal from '@/components/auth/staff/review-task/AccessRequestModal.vue'

import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('AccessRequestModal.vue', () => {
  let wrapper: any
  let wrapperFactory: any
  const props = {
    isRejectModal: false,
    isConfirmationModal: false,
    isSaving: false,
    isOnHoldModal: false,
    taskName: 'testprod',
    rejectReasonCodes: [
      {
        'code': 'BLANKAFFIDAVIT',
        'default': false,
        'desc': 'Affidavit is blank / affidavit is not attached'
      },
      {
        'code': 'REJECTACCOUNT',
        'default': false,
        'desc': 'Reject Account'
      }
    ]

  }

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({
      strict: false

    })

    wrapperFactory = (propsData) => {
      return mount(AccessRequestModal, {
        localVue,
        store,
        vuetify,
        propsData: {
          ...propsData
        }
      })
    }

    wrapper = wrapperFactory(props)
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('renders the components properly and address is being shown', () => {
    expect(wrapper.find(AccessRequestModal).exists()).toBe(true)
  })

  it('show Approval modal on open', async () => {
    await wrapper.vm.open()
    expect(wrapper.find('[data-test="dialog-header"]').text()).toBe(`Approve Account Creation Request ?`)
  })

  it('Should show reject modal on open when isRejectModal is true', async () => {
    await wrapper.setProps({ isRejectModal: true })
    await wrapper.vm.open()

    expect(wrapper.find('[data-test="dialog-header"]').text()).toBe(`Reject Account Creation Request ?`)
  })

  it('Should show on Hold modal on open when isOnHoldModal is true', async () => {
    await wrapper.setProps({ isOnHoldModal: true, isRejectModal: false })
    await wrapper.vm.open()

    expect(wrapper.find('[data-test="dialog-header"]').text()).toBe(`Reject or Hold Account Creation Request`)
  })

  it('Should show Approval modal for product ', async () => {
    await wrapper.setProps({ isOnHoldModal: false, isRejectModal: false, accountType: 'PRODUCT' })
    await wrapper.vm.open()

    expect(wrapper.find('[data-test="dialog-header"]').text()).toBe(`Approve Access Request ?`)
  })

  it('Should show Reject modal for product ', async () => {
    await wrapper.setProps({ isOnHoldModal: false, isRejectModal: true, accountType: 'PRODUCT' })
    await wrapper.vm.open()

    expect(wrapper.find('[data-test="dialog-header"]').text()).toBe(`Reject Access Request ?`)
  })
})
