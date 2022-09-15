import { defineComponent, toRefs } from "@vue/composition-api";
import { Component, Emit, Prop, Vue } from "vue-property-decorator";
import { namespace } from "vuex-class";
const BusinessModule = namespace("business");
export default defineComponent({
  props: {
    dialog: { type: Boolean },
    attach: { type: String },
    xmlData: { default: "", type: String },
    submitActive: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const { dialog, attach, xmlData, submitActive } = toRefs(props);
    const resubmit = (): string => {
      return xmlData.value;
    };
    const emitClose = (): void => {};
    return { resubmit, emitClose };
  },
});
