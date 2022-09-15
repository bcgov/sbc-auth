import { defineComponent, ref } from "@vue/composition-api";
import { Component, Vue } from "vue-property-decorator";
export default defineComponent({
  props: {},
  setup(_props, ctx) {
    const steps = ref<Array<any>>([
      {
        id: "step-1-btn",
        step: 1,
        text: "Decide on a Business Type",
        to: "/home/decide-business",
      },
      {
        id: "step-2-btn",
        step: 2,
        text: "Request a Name",
        to: "/home/request-name",
      },
      {
        id: "step-3-btn",
        step: 3,
        text: "Register or Incorporate",
        to: "/home/incorporate-or-register",
      },
      {
        id: "step-4-btn",
        step: 4,
        text: "Maintain Your Business",
        to: "/home/maintain-business",
      },
    ]);
    const goTo = (step: any): void => {
      if (!isCurrentStep(step)) ctx.root.$router.push(step.to);
    };
    const nextStep = (): void => {
      const currentStepIndex = getCurrentStep();
      const nextStep = steps.value[currentStepIndex];
      ctx.root.$router.push(nextStep.to);
    };
    const isCurrentStep = (step: any): boolean => {
      return ctx.root.$route.path === step.to;
    };
    const getCurrentStep = (): number => {
      const route = ctx.root.$route.path;
      for (const path of steps.value) {
        if (path.to === route) {
          return path.step || 0;
        }
      }
    };
    return { steps, goTo, nextStep, isCurrentStep, getCurrentStep };
  },
});
