import { defineComponent, toRefs, PropType } from "@vue/composition-api";
import Component from "vue-class-component";
import { Prop } from "vue-property-decorator";
import Vue from "vue";
export default defineComponent({
  name: "Steppable",
  props: {
    stepForward: { type: Object as PropType<(useAlternate?: boolean) => void> },
    stepBack: { type: Object as PropType<(useAlternate?: boolean) => void> },
    jumpToStep: {
      type: Object as PropType<(index: number, useAlternate?: boolean) => void>,
    },
  },
  setup(props, ctx) {
    const { stepForward, stepBack, jumpToStep } = toRefs(props);
    return {};
  },
});
