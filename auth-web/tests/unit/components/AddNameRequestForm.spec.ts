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
    expect(wrapper.find('[data-test="nr-number"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="applicant-phone-number"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="applicant-email"]').exists()).toBe(true)

    // verify buttons
    expect(wrapper.find('[data-test="forgot-button"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="add-button"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="add-button"]').attributes('disabled')).toBeDefined()
    expect(wrapper.find('[data-test="cancel-button"]').exists()).toBe(true)

    wrapper.destroy()
  })

  // Name Request number validation
  it('verifies nr input valid', async () => {
    const wrapper = wrapperFactory()
    wrapper.vm.applicantPhoneNumber = '250-123-4567'
    wrapper.vm.applicantEmail = '123@test.com'
    wrapper.vm.nrNumber = 'NR 1234567'
    await flushPromises()

    expect(wrapper.vm.nrNumber).toEqual('NR 1234567')
    expect(wrapper.vm.isFormValid()).toBe(true)
  })

  it('verifies nr input valid', async () => {
    const wrapper = wrapperFactory()
    wrapper.vm.applicantPhoneNumber = '250-123-4567'
    wrapper.vm.applicantEmail = '123@test.com'
    wrapper.vm.nrNumber = '1234567'
    await flushPromises()

    expect(wrapper.vm.nrNumber).toEqual('NR 1234567')
    expect(wrapper.vm.isFormValid()).toBe(true)
  })

  it('verifies nr input valid', async () => {
    const wrapper = wrapperFactory()
    wrapper.vm.applicantPhoneNumber = '250-123-4567'
    wrapper.vm.applicantEmail = '123@test.com'
    wrapper.vm.nrNumber = 'NR    1234567'
    await flushPromises()

    expect(wrapper.vm.nrNumber).toEqual('NR 1234567')
    expect(wrapper.vm.isFormValid()).toBe(true)
  })

  it('verifies nr input invalid', async () => {
    const wrapper = wrapperFactory()
    wrapper.vm.applicantPhoneNumber = '250-123-4567'
    wrapper.vm.applicantEmail = '123@test.com'
    wrapper.vm.nrNumber = 'NR 123456'
    await flushPromises()

    expect(wrapper.vm.isFormValid()).toBe(false)
  })

  it('verifies nr input invalid', async () => {
    const wrapper = wrapperFactory()
    wrapper.vm.applicantPhoneNumber = '250-123-4567'
    wrapper.vm.applicantEmail = '123@test.com'
    wrapper.vm.nrNumber = '   NR 1234567'
    await flushPromises()

    expect(wrapper.vm.isFormValid()).toBe(false)
  })
})
