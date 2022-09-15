import { defineComponent } from "@vue/composition-api";
import { Component, Mixins, Prop, Vue } from "vue-property-decorator";
import Steppable from "@/components/auth/common/stepper/Steppable.vue";
export default defineComponent({
  name: "StepperStub",
  props: {},
  setup(_props, ctx) {
    const next = () => {
      stepForward();
    };
    const nextWithAlternate = () => {
      stepForward(true);
    };
    const back = () => {
      stepBack();
    };
    const jumpToLast = () => {
      jumpToStep(3);
    };
    return { next, nextWithAlternate, back, jumpToLast };
  },
});
