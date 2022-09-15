import { defineComponent, toRefs } from "@vue/composition-api";
import { Component, Emit, Prop, Vue } from "vue-property-decorator";
import ProductTos from "@/components/auth/common/ProductTOS.vue";
export default defineComponent({
  components: {
    ProductTos,
  },
  props: {
    tabNumber: { default: null, type: Number },
    title: { default: "Agreement", type: String },
    userName: { default: "", type: String },
    orgName: { default: "", type: String },
    isTOSAlreadyAccepted: { default: true, type: Boolean },
    isApprovalFlow: { default: true, type: Boolean },
  },
  setup(props, ctx) {
    const {
      tabNumber,
      title,
      userName,
      orgName,
      isTOSAlreadyAccepted,
      isApprovalFlow,
    } = toRefs(props);
    return {};
  },
});
