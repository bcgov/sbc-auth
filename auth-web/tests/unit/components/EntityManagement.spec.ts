import '../test-utils/composition-api-setup' // important to import this first
import { createLocalVue, mount } from '@vue/test-utils'
import { useBusinessStore, useOrgStore, useUserStore } from '@/stores'
import { CorpTypes } from '@/util/constants'
import EntityManagement from '@/components/auth/manage-business/EntityManagement.vue'
import { RemoveBusinessPayload } from '@/models/Organization'
import Vue from 'vue'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'
import { setupIntersectionObserverMock } from '../util/helper-functions'

const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

function getPayLoad (type: any) {
  const removeNRPayload: RemoveBusinessPayload = {
    business: {
      corpType: {
        code: type as CorpTypes,
        desc: type as string
      },
      businessIdentifier: 'test',
      folioNumber: 'test'
    },
    orgIdentifier: 10
  }
  return removeNRPayload
}

describe('Entity Management Component', () => {
  setupIntersectionObserverMock()
  let wrapper: any
  let mockedNrMethod: any

  beforeEach(() => {
    const localVue = createLocalVue()
    const $t = () => 'test'

    const orgStore = useOrgStore()
    orgStore.currentOrganization = {
      name: 'new org',
      orgType: 'STAFF'
    } as any

    const userStore = useUserStore()
    userStore.currentUser = {
      firstName: 'Nadia',
      lastName: 'Woodie'
    } as any

    wrapper = mount(EntityManagement, {
      vuetify,
      localVue,
      mocks: { $t },
      computed: {
        enableBcCccUlc () {
          return true
        }
      }
    })
    mockedNrMethod = vi.fn()
    wrapper.vm.$refs.removalConfirmDialog.open = mockedNrMethod
  })

  afterEach(() => {
    wrapper.destroy()
    vi.resetModules()
    vi.clearAllMocks()
  })

  it('EntityManagement is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('EntityManagement contains removalConfirmDialog modal', () => {
    const modal = wrapper.find({ ref: 'removalConfirmDialog' })
    expect(modal.exists()).toBe(true)
  })

  it('EntityManagement contains businessUnavailableDialog modal', () => {
    const modal = wrapper.find({ ref: 'businessUnavailableDialog' })
    expect(modal.exists()).toBe(true)
  })

  it('calls the nr open modal with correct buttons', async () => {
    const removeNRPayload = getPayLoad('NR')
    wrapper.vm.showConfirmationOptionsModal(removeNRPayload)
    expect(mockedNrMethod).toHaveBeenCalled()
    expect(wrapper.vm.primaryBtnText).toBe('Remove Name Request')
    expect(wrapper.vm.secondaryBtnText).toBe('Keep Name Request')
  })
  it('calls the IA open modal with correct buttons', async () => {
    const removeBusinessPayload: RemoveBusinessPayload = getPayLoad('TMP')
    wrapper.vm.showConfirmationOptionsModal(removeBusinessPayload)
    expect(mockedNrMethod).toHaveBeenCalled()
    expect(wrapper.vm.primaryBtnText).toBe('Delete Incorporation Application')
    expect(wrapper.vm.secondaryBtnText).toBe('Keep Incorporation Application')
  })
  it('calls the Passcode reset open modal with correct buttons', async () => {
    const removeBusinessPayload: RemoveBusinessPayload = getPayLoad('CP')
    const mockedPasscodeResetMethod = vi.fn()
    wrapper.vm.$refs.passcodeResetOptionsModal.open = mockedPasscodeResetMethod
    wrapper.vm.showConfirmationOptionsModal(removeBusinessPayload)
    expect(mockedNrMethod).toHaveBeenCalledTimes(0)
    expect(mockedPasscodeResetMethod).toHaveBeenCalled()
  })
  it('calls the IA open modal with correct buttons', async () => {
    const removeBusinessPayload: RemoveBusinessPayload = getPayLoad('SP')
    wrapper.vm.showConfirmationOptionsModal(removeBusinessPayload)
    expect(mockedNrMethod).toHaveBeenCalled()
    expect(wrapper.vm.primaryBtnText).toBe('Remove Registration')
    expect(wrapper.vm.secondaryBtnText).toBe('Keep Registration')
  })
  it('calls the IA open modal with correct buttons', async () => {
    const removeBusinessPayload: RemoveBusinessPayload = getPayLoad('GP')
    wrapper.vm.showConfirmationOptionsModal(removeBusinessPayload)
    expect(mockedNrMethod).toHaveBeenCalled()
    expect(wrapper.vm.primaryBtnText).toBe('Remove Registration')
    expect(wrapper.vm.secondaryBtnText).toBe('Keep Registration')
  })

  it('Should render the #get-started-button element', async () => {
    expect(wrapper.find('#get-started-button').exists()).toBe(true)
  })

  it('calls the nr success modal', async () => {
    const mockedSyncBusinesses = vi.fn()
    wrapper.vm.syncBusinesses = mockedSyncBusinesses
    const mockedSearchNRIndex = vi.fn().mockReturnValue(0)
    wrapper.vm.searchNRIndex = mockedSearchNRIndex
    wrapper.vm.showAddSuccessModalNR('NR 1111111')
    await flushPromises()

    expect(mockedSyncBusinesses).toHaveBeenCalled()
    expect(mockedSearchNRIndex).toHaveBeenCalled()
    expect(wrapper.vm.snackbarText).toBe('NR 1111111 was successfully added to your table.')
  })

  it('calls the nr error modal', async () => {
    const mockedNrErrorMethod = vi.fn()
    wrapper.vm.$refs.errorDialog.open = mockedNrErrorMethod
    wrapper.vm.showNRErrorModal()
    expect(wrapper.vm.dialogTitle).toBe('Error Adding Name Request')
    expect(wrapper.vm.dialogText).toBe(
      'We couldn\'t find a name request associated with the phone number or email address you entered. Please try again.'
    )
    expect(mockedNrErrorMethod).toHaveBeenCalled()
  })

  it('renders snackbar visible 1 second after toggled', async () => {
    const businessStore = useBusinessStore()
    businessStore.syncBusinesses = vi.fn()
    vi.useFakeTimers()

    await wrapper.vm.showAddSuccessModalNR()
    vi.advanceTimersByTime(1000)
    await Vue.nextTick()

    expect(wrapper.find('#success-nr-business-snackbar').exists()).toBe(true)
    expect(wrapper.vm.showSnackbar).toBe(true)

    vi.clearAllTimers()
  })

  it('renders snackbar invisible 5 seconds after toggled', async () => {
    const businessStore = useBusinessStore()
    businessStore.syncBusinesses = vi.fn()
    vi.useFakeTimers()

    await wrapper.vm.showAddSuccessModalNR()
    vi.advanceTimersByTime(5000)
    await Vue.nextTick()

    expect(wrapper.find('#success-nr-business-snackbar').exists()).toBe(true)
    expect(wrapper.vm.showSnackbar).toBe(false)

    vi.clearAllTimers()
  })

  it('calls the link expired modal with correct title and message', () => {
    const name = 'Test Business'
    wrapper.vm.showLinkExpiredModal(name)
    expect(wrapper.vm.dialogTitle).toBe('Link Expired')
    expect(wrapper.vm.dialogText).toBe(`Your authorization request to manage ${name} has expired. Please try again.`)
  })

  it('calls the authorization error modal with correct title and message', () => {
    wrapper.vm.showAuthorizationErrorModal()
    expect(wrapper.vm.dialogTitle).toBe('Unable to Manage Business')
    expect(wrapper.vm.dialogText).toBe('The account that requested authorisation does not match your current account.' +
    ' Please log in as the account that initiated the request.')
  })

  it('calls the magic link error modal with correct title and message', () => {
    wrapper.vm.showMagicLinkErrorModal()
    expect(wrapper.vm.dialogTitle).toBe('Error Adding a Business to Your Account')
    expect(wrapper.vm.dialogText).toBe('An error occurred adding your business. Please try again.')
  })

  it('Should set the correct values when showNRNotFoundModal(label) is called', () => {
    const label = 'Password'
    wrapper.vm.showInvalidCodeModal(label)
    expect(wrapper.vm.showManageBusinessDialog).toBe(false)
    expect(wrapper.vm.dialogTitle).toBe(`Invalid ${label}`)
    expect(wrapper.vm.dialogText).toBe(`Unable to add the business. The provided ${label.toLowerCase()} is invalid.`)
  })

  it('Should set the correct values when showEntityNotFoundModal(label) is called', () => {
    const label = 'Password'
    wrapper.vm.showEntityNotFoundModal(label)
    expect(wrapper.vm.showManageBusinessDialog).toBe(false)
    expect(wrapper.vm.dialogTitle).toBe('Business Not Found')
    expect(wrapper.vm.dialogText).toBe('The specified business was not found.')
  })

  it('Should set the correct values when showBusinessAlreadyAdded(event) is called', () => {
    const event = {
      name: 'test',
      identifier: 'test'
    }
    const businessNameText = event.name ? `${event.name}` : ''
    wrapper.vm.showBusinessAlreadyAdded(event)
    expect(wrapper.vm.showManageBusinessDialog).toBe(false)
    expect(wrapper.vm.dialogTitle).toBe('Business Already Added')
    expect(wrapper.vm.dialogText).toBe(
      `The business ${businessNameText} with the business number ${event.identifier} is already in your Business Registry List.`
    )
  })

  it('Should set the correct values when showPasscodeClaimedModal() is called', () => {
    const contactNumber = 'test'
    wrapper.vm.showPasscodeClaimedModal()
    expect(wrapper.vm.dialogTitle).toBe('Passcode Already Claimed')
    expect(wrapper.vm.dialogText).toBe(`This passcode has already been claimed. If you have questions, please call ${contactNumber}`)
  })

  it('Should set the correct values when showUnknownErrorModal(type) is called', () => {
    let type = 'business'
    wrapper.vm.showUnknownErrorModal(type)
    expect(wrapper.vm.showManageBusinessDialog).toBe(false)
    expect(wrapper.vm.dialogTitle).toBe('Error Adding Existing Business')
    expect(wrapper.vm.dialogText).toBe('An error occurred adding your business. Please try again.')
    type = 'nr'
    wrapper.vm.showUnknownErrorModal(type)
    expect(wrapper.vm.dialogTitle).toBe('Error Adding Existing Name Request')
    expect(wrapper.vm.dialogText).toBe(
      'We couldn\'t find a name request associated with the phone number or email address you entered. Please try again.'
    )
    type = 'other'
    wrapper.vm.showUnknownErrorModal(type)
    expect(wrapper.vm.dialogTitle).toBe('Something Went Wrong')
    expect(wrapper.vm.dialogText).toBe('An error occurred, please try again. If this error persists, please contact us.')
  })

  it('Should set the correct values when showNRNotFoundModal() is called', () => {
    wrapper.vm.showNRNotFoundModal()
    expect(wrapper.vm.dialogTitle).toBe('Name Request Not Found')
    expect(wrapper.vm.dialogText).toBe('The specified name request was not found.')
  })

  it('Should set the correct values when showCreateAffiliationInvitationErrorDialog() is called', () => {
    wrapper.vm.showCreateAffiliationInvitationErrorDialog()
    expect(wrapper.vm.dialogTitle).toBe('Error Sending Authorization Email')
    expect(wrapper.vm.dialogText).toBe('An error occurred sending authorization email. Please try again.')
  })

  it('Should set the correct values when showBusinessUnavailableModal(action) is called', () => {
    let action = 'test'
    wrapper.vm.showBusinessUnavailableModal(action)
    expect(wrapper.vm.dialogTitle).toBe('Business Unavailable')
    expect(wrapper.vm.dialogText).toBe(
      'You are not authorized to access the business you wish to test. Please add this business to your table to continue.'
    )
    action = 'change name'
    wrapper.vm.showBusinessUnavailableModal(action)
    expect(wrapper.vm.dialogTitle).toBe('Business Unavailable')
    expect(wrapper.vm.dialogText).toBe(
      'You are not authorized to access the business to change its name. Please add this business to your table to continue.'
    )
  })

  it('Should set the correct values when showAddBusinessModal() is called', () => {
    wrapper.vm.showAddBusinessModal()
    expect(wrapper.vm.showManageBusinessDialog).toBe(true)
  })

  it('Should set the correct values when populateNRmodalValues() is called', () => {
    wrapper.vm.populateNRmodalValues()
    expect(wrapper.vm.primaryBtnText).toBe('Remove Name Request')
    expect(wrapper.vm.secondaryBtnText).toBe('Keep Name Request')
  })

  it('Should set the correct values when populateIAmodalValues() is called', () => {
    wrapper.vm.populateIAmodalValues()
    expect(wrapper.vm.primaryBtnText).toBe('Delete Incorporation Application')
    expect(wrapper.vm.secondaryBtnText).toBe('Keep Incorporation Application')
  })

  it('Should set the correct values when populateRegistrationModalValues() is called', () => {
    wrapper.vm.populateRegistrationModalValues()
    expect(wrapper.vm.primaryBtnText).toBe('Delete Registration')
    expect(wrapper.vm.secondaryBtnText).toBe('Keep Registration')
  })

  it('Should set the correct values when populateFirmModalValues() is called', () => {
    wrapper.vm.populateFirmModalValues()
    expect(wrapper.vm.primaryBtnText).toBe('Remove Registration')
    expect(wrapper.vm.secondaryBtnText).toBe('Keep Registration')
  })
})
