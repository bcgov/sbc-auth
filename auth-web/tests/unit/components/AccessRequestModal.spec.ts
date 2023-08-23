import '@/composition-api-setup'
import { createLocalVue, mount } from '@vue/test-utils'
import AccessRequestModal from '@/components/auth/staff/review-task/AccessRequestModal.vue'
import { OnholdOrRejectCode } from '@/util/constants'
import VueCompositionAPI from '@vue/composition-api'
import Vuetify from 'vuetify'
import initialize from '@/plugins/i18n'

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('AccessRequestModal.vue', () => {
  let wrapper: any
  let wrapperFactory: any
  let accessRequest: any
  const props = {
    isRejectModal: false,
    isConfirmationModal: false,
    isSaving: false,
    isOnHoldModal: false,
    taskName: 'testprod',
    onholdReasons: [
      {
        'code': 'BLANKAFFIDAVIT',
        'default': false,
        'desc': 'Affidavit is blank / affidavit is not attached'
      },
      {
        'code': 'MISSINGSEAL',
        'default': false,
        'desc': 'Affidavit is missing seal'
      }
    ]

  }

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(VueCompositionAPI)
    const i18n = initialize(localVue)

    const $t = () =>
      `To place account on hold, please choose a reason. An email will be sent to the user to 
      resolve the issue. Or choose "Reject Account"`

    wrapperFactory = (propsData) => {
      return mount(AccessRequestModal, {
        localVue,
        vuetify,
        i18n,
        propsData: {
          ...propsData
        },
        mocks: { $t }
      })
    }

    wrapper = wrapperFactory(props)
    accessRequest = wrapper.findComponent({ ref: 'accessRequest' })
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the components properly and address is being shown', () => {
    expect(wrapper.findComponent(AccessRequestModal).exists()).toBe(true)
  })

  it('show Approval modal on open', async () => {
    await accessRequest.vm.open()
    expect(wrapper.find('[data-test="dialog-header"]').text()).toBe(`Approve Account Creation Request ?`)
  })

  it('Should show reject modal on open when isRejectModal is true', async () => {
    await wrapper.setProps({ isRejectModal: true })
    await accessRequest.vm.open()

    expect(wrapper.find('[data-test="dialog-header"]').text()).toBe(`Reject Account Creation Request ?`)
  })

  it('Should show on Hold modal on open when isOnHoldModal is true', async () => {
    await wrapper.setProps({ isOnHoldModal: true, isRejectModal: false })
    await accessRequest.vm.open()

    expect(wrapper.find('[data-test="dialog-header"]').text()).toBe(`Reject or Hold Account Creation Request`)
  })

  it('Should show Approval modal for product ', async () => {
    await wrapper.setProps({ isOnHoldModal: false, isRejectModal: false, accountType: 'PRODUCT' })
    await accessRequest.vm.open()

    expect(wrapper.find('[data-test="dialog-header"]').text()).toBe(`Approve Access Request ?`)
  })

  it('Should show Reject modal for product ', async () => {
    await wrapper.setProps({ isOnHoldModal: false, isRejectModal: true, accountType: 'PRODUCT' })
    await accessRequest.vm.open()

    expect(wrapper.find('[data-test="dialog-header"]').text()).toBe(`Reject Access Request ?`)
  })

  it('render on hold reasons properly ', async () => {
    await wrapper.setProps({ isOnHoldModal: true, isRejectModal: false })
    await accessRequest.vm.open()

    expect(wrapper.vm.accountToBeOnholdOrRejected).toBe('')

    await wrapper.find('[data-test="radio-reject"]').trigger('click')
    expect(wrapper.vm.accountToBeOnholdOrRejected).toBe(OnholdOrRejectCode.REJECTED)
    await wrapper.find('[data-test="radio-on-hold"]').trigger('click')
    expect(wrapper.vm.accountToBeOnholdOrRejected).toBe(OnholdOrRejectCode.ONHOLD)

    expect(wrapper.find('[data-test="hold-reason-type"]').exists()).toBe(true)
  })

  it('emit valid on hold reasons properly ', async () => {
    await wrapper.setProps({ isOnHoldModal: true, isRejectModal: false })
    await accessRequest.vm.open()

    await wrapper.find('[data-test="radio-on-hold"]').trigger('click')
    expect(wrapper.vm.accountToBeOnholdOrRejected).toBe(OnholdOrRejectCode.ONHOLD)

    const remarks = 'Affidavit is missing seal'
    const select = wrapper.find('[data-test="hold-reason-type"]')
    await select.setValue(remarks)
    expect(wrapper.vm.onholdReasons).toBe(remarks)

    const rejectFormMock = {
      validate: () => true
    }
    await wrapper.setData({ rejectForm: rejectFormMock })
    await wrapper.vm.$nextTick()
    await wrapper.find('[data-test="btn-access-request"]').trigger('click')
    expect(wrapper.emitted('approve-reject-action')).toBeTruthy()
  })
})
