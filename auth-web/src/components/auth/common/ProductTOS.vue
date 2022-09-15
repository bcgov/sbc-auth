import {
  defineComponent,
  toRefs,
  ref,
  watch,
  onMounted,
} from "@vue/composition-api";
import { Component, Emit, Prop, Vue, Watch } from "vue-property-decorator";
import { OrgProduct } from "@/models/Organization";
import { productStatus } from "@/util/constants";
export default defineComponent({
  props: {
    userName: { default: "", type: String },
    orgName: { default: "", type: String },
    isTOSAlreadyAccepted: { default: false, type: Boolean },
    isApprovalFlow: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const { userName, orgName, isTOSAlreadyAccepted, isApprovalFlow } =
      toRefs(props);
    const termsAccepted = ref<boolean>(false);
    const istosTouched = ref<boolean>(false);
    const onisTOSALreadyAcceptedChange = (newTos: boolean, oldTos: boolean) => {
      if (newTos !== oldTos) {
        termsAccepted.value = newTos;
      }
    };
    const tosChanged = () => {
      istosTouched.value = true;
      return termsAccepted.value;
    };
    watch(isTOSAlreadyAccepted, onisTOSALreadyAcceptedChange);
    onMounted(() => {
      termsAccepted.value = isTOSAlreadyAccepted.value;
    });
    return {
      termsAccepted,
      istosTouched,
      onisTOSALreadyAcceptedChange,
      tosChanged,
    };
  },
});
