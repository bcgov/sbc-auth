import { mount, shallowMount } from '@vue/test-utils'
import AddNameRequestForm from '@/components/auth/manage-business/AddNameRequestForm.vue'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Add Name Request Form', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    wrapperFactory = (props: any) => {
      return mount(AddNameRequestForm, {
        mocks: {
          $t: (msg) => msg
        },
        propsData: {
          props
        },
        vuetify
      })
    }

    wrapper = wrapperFactory()
  })

  it('renders the component properly', () => {
    const wrapper = shallowMount(AddNameRequestForm, {
      vuetify,
      propsData: { dialog: true }
    })

    // verify components
    expect(wrapper.attributes('class')).toBe('add-namerequest-form')
    expect(wrapper.find('.add-namerequest-form').isVisible()).toBe(true)
    expect(wrapper.findComponent(HelpDialog).exists()).toBe(true)

    // verify input fields
    expect(wrapper.find('[data-test="applicant-phone-number"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="applicant-email"]').exists()).toBe(true)

    // verify buttons
    expect(wrapper.find('[data-test="forgot-button"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="add-button"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="add-button"]').attributes('disabled')).toBeDefined()
    expect(wrapper.find('[data-test="cancel-button"]').exists()).toBe(true)

    wrapper.destroy()
  })

  // Applicant phone number validation
  it('verifies phone input valid', async () => {
    wrapper.vm.applicantPhoneNumber = '250-123-4567'
    wrapper.vm.applicantEmail = ''
    await flushPromises()

    expect(wrapper.vm.applicantPhoneNumber).toEqual('250-123-4567')
    expect(wrapper.vm.applicantPhoneNumberRules.every(rule => rule(wrapper.vm.applicantPhoneNumber) === true)).toBe(true)
  })

  it('verifies phone input invalid', async () => {
    wrapper.vm.applicantPhoneNumber = '250-123-456-789'
    wrapper.vm.applicantEmail = ''
    await flushPromises()

    expect(wrapper.vm.applicantPhoneNumberRules.some(rule => rule(wrapper.vm.applicantPhoneNumber) !== true)).toBe(true)
  })

  // Applicant email validation
  it('verifies email input valid', async () => {
    wrapper.vm.applicantPhoneNumber = ''
    wrapper.vm.applicantEmail = '123@test.com'
    await flushPromises()

    expect(wrapper.vm.applicantEmail).toEqual('123@test.com')
    expect(wrapper.vm.applicantEmailRules.every(rule => rule(wrapper.vm.applicantEmail) === true)).toBe(true)
  })

  it('verifies email input invalid', async () => {
    wrapper.vm.applicantPhoneNumber = ''
    wrapper.vm.applicantEmail = '123@test'
    await flushPromises()

    expect(wrapper.vm.applicantEmailRules.some(rule => rule(wrapper.vm.applicantEmail) !== true)).toBe(true)
  })
})
