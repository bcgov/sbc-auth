import { createLocalVue, mount } from '@vue/test-utils'
import Stepper from '@/components/auth/common/stepper/Stepper.vue'
import Vuetify from 'vuetify'

describe('Stepper.vue', () => {
  let wrapper: any

  beforeEach(() => {
    const localVue = createLocalVue()

    const vuetify = new Vuetify({})

    wrapper = mount(Stepper, {
      localVue,
      vuetify
    })

    vi.resetModules()
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('is default configurations are correct', () => {
    expect(wrapper.vm.defaultSteps.length).toBe(3)
  })

  it('is renders correctly', () => {
    expect(wrapper.find('.stepper')).toBeTruthy()
    expect(wrapper.find('.stepper-nav')).toBeTruthy()
    expect(wrapper.find('.stepper-content')).toBeTruthy()
  })

  it('is renders correct number of steps', () => {
    expect(wrapper.findAll('.stepper-nav .v-stepper__step').length).toBe(wrapper.vm.defaultSteps.length)
  })

  it('is selects the 1st step initially', () => {
    expect(wrapper.vm.currentStep).toBe(wrapper.vm.defaultSteps[0])
  })

  it('is gets step title and name correctly', () => {
    const firstStep = wrapper.vm.defaultSteps[0]
    expect(wrapper.vm.getStepTitle(firstStep)).toBe(firstStep.title)
    expect(wrapper.vm.getStepName(firstStep)).toBe(firstStep.stepName)
  })

  it('is gets step props', () => {
    const firstStep = wrapper.vm.defaultSteps[0]
    const stepProp = {
      stepForward: vi.fn(),
      stepBack: vi.fn(),
      jumpToStep: vi.fn()
    }
    const props = Object.keys(wrapper.vm.getPropsForStep(firstStep))
    expect(props.length).toBe(Object.keys(stepProp).length)
  })

  it('is gets step index correctly', () => {
    const firstStep = wrapper.vm.defaultSteps[0]
    expect(wrapper.vm.getStepIndex(firstStep)).toBe(1)
  })

  it('is step forwards correctly', () => {
    expect(wrapper.vm.currentStepNumber).toBe(1)
    wrapper.vm.stepForward()
    expect(wrapper.vm.currentStepNumber).toBe(2)
  })

  it('is step backwards correctly', () => {
    wrapper.vm.currentStepNumber = 3
    wrapper.vm.stepBack()
    expect(wrapper.vm.currentStepNumber).toBe(2)
  })

  it('is jumping to step correctly', () => {
    wrapper.vm.jumpToStep(2)
    expect(wrapper.vm.currentStepNumber).toBe(2)
  })
})
