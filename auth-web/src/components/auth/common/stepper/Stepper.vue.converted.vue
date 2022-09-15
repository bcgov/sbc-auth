import {
  defineComponent,
  toRefs,
  ref,
  computed,
  onBeforeMount,
  PropType,
} from "@vue/composition-api";
import { Component, Emit, Prop } from "vue-property-decorator";
import StepperStub from "@/components/auth/common/stepper/StepperStub.vue";
import Vue from "vue";
export interface StepConfiguration {
  title: string;
  stepName: string;
  component: Vue.Component;
  componentProps: Record<string, any>;
  alternate?: StepConfiguration;
}
export default defineComponent({
  name: "Stepper",
  components: {
    StepperStub,
  },
  props: {
    stepperConfiguration: {
      default: null,
      type: Array as Proptype<StepConfiguration[]>,
    },
    redirectWhenDone: { default: "/business", type: String },
    isLoading: { default: false, type: Boolean },
    stepperColor: { default: "", type: String },
  },
  setup(props, ctx) {
    const { stepperConfiguration, redirectWhenDone, isLoading, stepperColor } =
      toRefs(props);
    const steps = ref<StepConfiguration[]>(undefined);
    const currentStepNumber = ref(1);
    const useAlternateStep = ref(false);
    const defaultSteps = computed((): Array<StepConfiguration> => {
      return [
        {
          title: "Step 1",
          stepName: "Step Name 1",
          component: StepperStub,
          componentProps: {},
        },
        {
          title: "Step 2",
          stepName: "Step Name 2",
          component: StepperStub,
          componentProps: {},
        },
        {
          title: "Step 3",
          stepName: "Step Name 3",
          component: StepperStub,
          componentProps: {},
        },
      ];
    });
    const currentStep = computed((): StepConfiguration => {
      const current = steps.value.find(
        (step) => getStepIndex(step) === currentStepNumber.value
      );
      return useAlternateStep.value ? current.alternate : current;
    });
    const getStepTitle = (step: StepConfiguration) => {
      return useAlternateStep.value &&
        currentStepNumber.value === getStepIndex(step)
        ? step.alternate?.title
        : step.title;
    };
    const getStepName = (step: StepConfiguration) => {
      return useAlternateStep.value &&
        currentStepNumber.value === getStepIndex(step)
        ? step.alternate?.stepName
        : step.stepName;
    };
    const getPropsForStep = (step: StepConfiguration): Record<string, any> => {
      return {
        ...step.componentProps,
        stepForward: stepForward,
        stepBack: stepBack,
        jumpToStep: jumpToStep,
      };
    };
    const getStepIndex = (step: StepConfiguration): number => {
      return steps.value.indexOf(step) + 1;
    };
    const stepForward = (useAlternateStep = false) => {
      if (currentStepNumber.value >= steps.value.length) {
        ctx.root.$router.push(redirectWhenDone.value);
      } else {
        useAlternateStep.value =
          useAlternateStep && !!steps.value[currentStepNumber.value].alternate;
        currentStepNumber.value++;
      }
    };
    const stepBack = (useAlternateStep = false) => {
      currentStepNumber.value = Math.max(1, currentStepNumber.value - 1);
      useAlternateStep.value =
        useAlternateStep &&
        !!steps.value[currentStepNumber.value - 1].alternate;
    };
    const jumpToStep = (index: number, useAlternateStep = false) => {
      if (index > 0 && index <= steps.value.length) {
        useAlternateStep.value =
          useAlternateStep && !!steps.value[index].alternate;
        currentStepNumber.value = index;
      }
    };
    const emitFinalStepAction = (stepperData) => {
      return stepperData;
    };
    onBeforeMount(async () => {
      steps.value = stepperConfiguration.value || defaultSteps.value;
    });
    return {
      steps,
      currentStepNumber,
      useAlternateStep,
      defaultSteps,
      currentStep,
      getStepTitle,
      getStepName,
      getPropsForStep,
      getStepIndex,
      stepForward,
      stepBack,
      jumpToStep,
      emitFinalStepAction,
    };
  },
});
