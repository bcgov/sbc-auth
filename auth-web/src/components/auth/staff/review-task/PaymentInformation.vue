import { defineComponent, toRefs, PropType } from "@vue/composition-api";
import { Component, Emit, Prop, Vue } from "vue-property-decorator";
import { GLInfo } from "@/models/Organization";
export default defineComponent({
  props: {
    tabNumber: { default: null, type: Number },
    currentOrganizationGLInfo: {
      default: null,
      type: Object as PropType<GLInfo>,
    },
    title: { default: "Payment Information", type: String },
  },
  setup(props, ctx) {
    const { tabNumber, currentOrganizationGLInfo, title } = toRefs(props);
    return {};
  },
});
