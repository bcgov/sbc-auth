import { defineComponent, toRefs } from "@vue/composition-api";
import { Component, Prop, Vue } from "vue-property-decorator";
export default defineComponent({
  props: {
    showPayWithOnlyCC: { default: false, type: Boolean },
    totalBalanceDue: { default: 0, type: Number },
    partialCredit: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const { showPayWithOnlyCC, totalBalanceDue, partialCredit } = toRefs(props);
    return {};
  },
});
