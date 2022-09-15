import {
  defineComponent,
  toRefs,
  ref,
  watch,
  onMounted,
  onUpdated,
  PropType,
} from "@vue/composition-api";
import {
  Component,
  Emit,
  Mixins,
  Prop,
  Vue,
  Watch,
} from "vue-property-decorator";
import { GLInfo } from "@/models/Organization";
import { mask } from "vue-the-mask";
import { namespace } from "vuex-class";
const OrgModule = namespace("org");
export default defineComponent({
  directives: {
    mask,
  },
  props: {
    glInformation: {
      default: () => ({} as GLInfo),
      type: Object as PropType<any>,
    },
    canSelect: { default: true, type: Boolean },
  },
  setup(props, ctx) {
    const { glInformation, canSelect } = toRefs(props);
    const client = ref<string>("");
    const responsibilityCentre = ref<string>("");
    const serviceLine = ref<string>("");
    const stob = ref<string>("");
    const projectCode = ref<string>("");
    const $refs = ref<{
      GlInfoForm: HTMLFormElement;
    }>(undefined);
    const clientRules = ref([
      (v) => !!v || "Client Code is required",
      (v) => v.length >= 3 || "Client Code should be 3 characters",
    ]);
    const responsibilityCentreRules = ref([
      (v) => !!v || "Responsibility Center is required",
      (v) => v.length === 5 || "Responsibility Center should be 5 characters",
    ]);
    const serviceLineRules = ref([
      (v) => !!v || "Account Number is required",
      (v) => v.length === 5 || "Account Number should be 5 characters",
    ]);
    const stobRules = ref([
      (v) => !!v || "Standard Object is required",
      (v) => v.length === 4 || "Standard Object should be 4 characters",
    ]);
    const projectCodeRules = ref([
      (v) => !!v || "Project is required",
      (v) => v.length === 7 || "Project should be 7 characters",
    ]);
    const oncurrentOrgGLInfoChange = (newGlInfo) => {
      setGlInfo(newGlInfo);
    };
    const setGlInfo = (glInfo) => {
      client.value = glInfo?.client || "";
      responsibilityCentre.value = glInfo?.responsibilityCentre || "";
      serviceLine.value = glInfo?.serviceLine || "";
      stob.value = glInfo?.stob || "";
      projectCode.value = glInfo?.projectCode || "";
    };
    const emitGLInfo = async () => {
      const glInfo: GLInfo = {
        client: client.value,
        responsibilityCentre: responsibilityCentre.value,
        serviceLine: serviceLine.value,
        stob: stob.value,
        projectCode: projectCode.value,
      };
      isGlInfoFormValid();
      setCurrentOrganizationGLInfo(glInfo);
      return glInfo;
    };
    const isGlInfoFormValid = () => {
      return ctx.refs.GlInfoForm?.validate() || false;
    };
    watch(currentOrgGLInfo, oncurrentOrgGLInfoChange);
    onMounted(() => {
      const glInfo: GLInfo = Object.keys(glInformation.value).length
        ? glInformation.value
        : currentOrgGLInfo;
      setGlInfo(glInfo);
    });
    onUpdated(() => {
      isGlInfoFormValid();
    });
    return {
      client,
      responsibilityCentre,
      serviceLine,
      stob,
      projectCode,
      $refs,
      clientRules,
      responsibilityCentreRules,
      serviceLineRules,
      stobRules,
      projectCodeRules,
      oncurrentOrgGLInfoChange,
      setGlInfo,
      emitGLInfo,
      isGlInfoFormValid,
    };
  },
});
