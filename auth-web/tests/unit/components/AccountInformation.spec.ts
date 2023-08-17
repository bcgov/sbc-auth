
import { AccessType, AccountStatus } from '@/util/constants'
import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import { getTestAddress, getTestOrg } from '../test-utils'
import { AccountInformation } from '@/components/auth/staff/review-task'
import { OrgAccountTypes } from '@/models/Organization'
import Vue from 'vue'
import VueCompositionAPI from '@vue/composition-api'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import flushPromises from 'flush-promises'

// @ts-ignore
Vue.use(VueCompositionAPI)
Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('AccountInformation.vue basic tests', () => {
  let wrapper: Wrapper<any>

  const props = {
    tabNumber: 2,
    title: 'Account Information',
    accountUnderReview: getTestOrg(),
    accountUnderReviewAddress: getTestAddress()
  }

  const updateForGovnReview = async () => {
    const params = { accessType: AccessType.GOVN, orgType: OrgAccountTypes.GOVN, statusCode: AccountStatus.PENDING_STAFF_REVIEW }
    wrapper.setProps({
      accountUnderReview: getTestOrg(params),
      isGovnReview: true
    })
    await Vue.nextTick()
  }

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const store = new Vuex.Store({
      strict: false
    })

    wrapper = mount(AccountInformation, {
      localVue,
      store,
      vuetify,
      propsData: {
        ...props
      }
    })
  })

  afterEach(() => { wrapper.destroy() })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the components properly ', () => {
    expect(wrapper.findComponent(AccountInformation).exists()).toBe(true)
  })

  it('renders proper header content', () => {
    expect(wrapper.find('h2').text()).toBe(`${props.tabNumber}. ${props.title}`)
  })

  it('does not show access type (only for GOVN review)', () => {
    expect(wrapper.find('.access-type').exists()).toBe(false)
  })

  it('shows access type for GOVN review', async () => {
    await updateForGovnReview()
    expect(wrapper.find('.access-type').exists()).toBe(true)
    expect(wrapper.find('.access-type p').text()).toBe('Access Type')
    // validation classes are not enabled
    expect(wrapper.find('.access-type.error-border').exists()).toBe(false)
    expect(wrapper.find('.access-type p.error-color').exists()).toBe(false)
    // correct access type displayed
    expect(wrapper.find('.access-type__desc').text()).toBe('Government agency (other than BC provincial)')
    // change btn showing
    expect(wrapper.find('.access-type button').text()).toBe('Change')
    // radio btns not showing
    expect(wrapper.find('.access-type__radio-grp').exists()).toBe(false)
    // update btns not showing
    expect(wrapper.findAll('.access-type button').length).toBe(1)
  })

  it('opens update view on change click for GOVN review', async () => {
    await updateForGovnReview()
    expect(wrapper.find('.access-type button').exists()).toBe(true)
    // click
    wrapper.find('.access-type button').trigger('click')
    await Vue.nextTick()
    // radio options show
    expect(wrapper.find('.access-type__radio-grp').exists()).toBe(true)
    const radioLabels = wrapper.findAll('.access-type__radio-grp .v-radio')
    expect(radioLabels.length).toBe(2)
    expect(radioLabels.at(0).text()).toBe('Regular Access')
    expect(radioLabels.at(0).attributes()['class']).not.toContain('v-item--active')
    expect(radioLabels.at(1).text()).toBe('Government agency (other than BC provincial)')
    expect(radioLabels.at(1).attributes()['class']).toContain('v-item--active')
    // update access btns show
    const buttons = wrapper.findAll('.access-type button')
    expect(buttons.length).toBe(2)
    expect(buttons.at(0).text()).toBe('Done')
    expect(buttons.at(1).text()).toBe('Cancel')
    // sets error validation for access type if showing
    wrapper.setProps({ showValidations: true })
    await Vue.nextTick()
    expect(wrapper.find('.access-type.error-border').exists()).toBe(true)
    expect(wrapper.find('.access-type p.error-color').exists()).toBe(true)
  })

  it('updates access type successfully', async () => {
    await updateForGovnReview()
    // click change
    wrapper.find('.access-type button').trigger('click')
    await Vue.nextTick()
    await wrapper.setData({ selectedAccessType: AccessType.REGULAR })
    await flushPromises()
    const radioOptions = wrapper.findAll('.access-type__radio-grp .v-radio')
    expect(radioOptions.at(0).attributes()['class']).toContain('v-item--active')
    expect(radioOptions.at(1).attributes()['class']).not.toContain('v-item--active')
    // click done
    const buttons = wrapper.findAll('.access-type button')
    buttons.at(0).trigger('click')
    await Vue.nextTick()
    // verify change
    expect(wrapper.find('.access-type__radio-grp').exists()).toBe(false)
    expect(wrapper.find('.access-type__desc').text()).toBe('Regular Access')
    expect(wrapper.emitted('emit-access-type')[0].length).toBe(1)
    expect(wrapper.emitted('emit-access-type')[0]).toEqual([AccessType.REGULAR])
    // undo change
    const button = wrapper.find('.access-type button')
    expect(button.exists()).toBe(true)
    expect(button.text()).toBe('Undo')
    button.trigger('click')
    await Vue.nextTick()
    // verify changed back
    expect(wrapper.find('.access-type__desc').text()).toBe('Government agency (other than BC provincial)')
    expect(wrapper.find('.access-type button').text()).toBe('Change')
  })
})
