import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import DissolutionSchedule from '@/components/auth/staff/DissolutionSchedule.vue'
import { InvoluntaryDissolutionConfigNames } from '@/util/constants'
import StaffService from '../../../src/services/staff.services'
import Vue from 'vue'
import Vuetify from 'vuetify'
import { useStaffStore } from '@/stores'

describe('DissolutionSchedule.vue', () => {
  let wrapper: Wrapper<any>

  beforeEach(() => {
    const localVue = createLocalVue()

    vi.spyOn((StaffService as any), 'getInvoluntaryDissolutionBatchSize').mockImplementation(() => ({}))

    const staffStore = useStaffStore()
    staffStore.involuntaryDissolutionConfigurations = {
      configurations: [
        {
          'fullDescription': 'Number of involuntary dissolutions per day.',
          'name': InvoluntaryDissolutionConfigNames.NUM_DISSOLUTIONS_ALLOWED,
          'shortDescription': 'Number of involuntary dissolutions per day.',
          'value': '250'
        }
      ]
    }

    wrapper = mount(DissolutionSchedule, {
      localVue,
      vuetify: new Vuetify({})
    })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the component properly', () => {
    expect(wrapper.findComponent(DissolutionSchedule).exists()).toBe(true)
    expect(wrapper.find('#dissolution-schedule').isVisible()).toBe(true)
    expect(wrapper.find('#schedule-summary-label').exists()).toBe(true)
    expect(wrapper.find('.section-container').exists()).toBe(true)
  })

  it('shows the proper schedule summary text', async () => {
    await Vue.nextTick()
    expect(wrapper.find('#schedule-summary-label').text()).toBe('Schedule Summary')
    expect(wrapper.find('span').text()).toContain('Moving 250 businesses into D1 dissolution every Tuesday,')
    expect(wrapper.find('span').text()).toContain(' Wednesday, and Thursday at 12:15 a.m. Pacific Time.')
  })

  it('clicking on edit button shows the editing panel', async () => {
    // verify that proper components don't exist
    expect(wrapper.vm.isEdit).toBe(false)
    expect(wrapper.find('#dissolution-batch-size-label').exists()).toBe(false)
    expect(wrapper.find('#dissolution-batch-size-text-field').exists()).toBe(false)

    // verify Edit button and click it
    const editButton = wrapper.find('#edit-btn')
    expect(editButton.text()).toBe('Edit')
    await editButton.trigger('click')

    // verify that proper components exist and now are visible
    expect(wrapper.vm.isEdit).toBe(true)
    expect(wrapper.find('#dissolution-batch-size-label').isVisible()).toBe(true)
    expect(wrapper.find('#dissolution-batch-size-text-field').isVisible()).toBe(true)
  })

  it('clicking on cancel button closes the editing panel', async () => {
    // verify that proper components don't exist
    expect(wrapper.vm.isEdit).toBe(false)
    expect(wrapper.find('#cancel-btn').exists()).toBe(false)
    expect(wrapper.find('#dissolution-batch-size-label').exists()).toBe(false)
    expect(wrapper.find('#dissolution-batch-size-text-field').exists()).toBe(false)

    // Edit button clicked
    const editButton = wrapper.find('#edit-btn')
    await editButton.trigger('click')

    // verify that cancel button now exists and is visible
    expect(wrapper.find('#cancel-btn').isVisible()).toBe(true)

    // Cancel button clicked
    const cancelButton = wrapper.find('#cancel-btn')
    expect(cancelButton.text()).toBe('Cancel')
    await cancelButton.trigger('click')

    // verify that proper components don't exist anymore and are not shown
    expect(wrapper.vm.isEdit).toBe(false)
    expect(wrapper.find('#dissolution-batch-size-label').exists()).toBe(false)
    expect(wrapper.find('#dissolution-batch-size-text-field').exists()).toBe(false)
  })

  it('clicking on save button saves the batch size', async () => {
    expect(wrapper.find('#save-btn').exists()).toBe(false)

    // Edit button clicked
    const editButton = wrapper.find('#edit-btn')
    await editButton.trigger('click')

    // verify that save button now exists and is visible
    expect(wrapper.find('#save-btn').isVisible()).toBe(true)

    // set the batch size to 10 instead of 250
    const input = wrapper.find('#dissolution-batch-size-text-field')
    input.setValue('10')
    input.trigger('change')

    // Save button clicked
    const saveButton = wrapper.find('#save-btn')
    expect(saveButton.text()).toBe('Save')
    await saveButton.trigger('click')

    // the number is updated
    expect(wrapper.find('span').text()).toContain('Moving 10 businesses into D1 dissolution every Tuesday,')
  })
})
