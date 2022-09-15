import {
  defineComponent,
  toRefs,
  ref,
  watch,
  onMounted,
} from "@vue/composition-api";
import {
  Component,
  Emit,
  Mixins,
  Prop,
  Vue,
  Watch,
} from "vue-property-decorator";
import { OrgBusinessType, Organization } from "@/models/Organization";
import { Account } from "@/util/constants";
import AccountChangeMixin from "@/components/auth/mixins/AccountChangeMixin.vue";
import { Code } from "@/models/Code";
import { namespace } from "vuex-class";
const OrgModule = namespace("org");
const CodesModule = namespace("codes");
export default defineComponent({
  components: {},
  props: {
    errorMessage: { default: null, type: String },
    saving: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const { errorMessage, saving } = toRefs(props);
    const isLoading = ref(false);
    const $refs = ref<{
      businessType: HTMLFormElement;
      businessSize: HTMLFormElement;
    }>(undefined);
    const businessType = ref("");
    const businessSize = ref("");
    const orgBusinessTypeRules = ref([
      (v) => !!v || "A business type is required",
    ]);
    const orgBusinessSizeRules = ref([
      (v) => !!v || "A business size is required",
    ]);
    const emitUpdatedOrgBusinessType = () => {
      const orgBusinessType: OrgBusinessType = {
        businessType: businessType.value,
        businessSize: businessSize.value,
      };
      return orgBusinessType;
    };
    const emitValid = () => {
      return (
        !ctx.refs.businessType?.hasError && !ctx.refs.businessSize?.hasError
      );
    };
    const setup = async () => {
      try {
        isLoading.value = true;
        await getBusinessSizeCodes();
        await getBusinessTypeCodes();
        businessType.value = currentOrganization.businessType;
        businessSize.value = currentOrganization.businessSize;
      } catch (ex) {
        console.log(`error while loading account business type -  ${ex}`);
      } finally {
        isLoading.value = false;
      }
    };
    const onOrgBusinessTypeChange = async () => {
      await ctx.root.$nextTick();
      emitUpdatedOrgBusinessType();
      emitValid();
    };
    watch(businessType, onOrgBusinessTypeChange);
    onMounted(async () => {
      setAccountChangedHandler(setup);
      await setup();
    });
    return {
      isLoading,
      $refs,
      businessType,
      businessSize,
      orgBusinessTypeRules,
      orgBusinessSizeRules,
      emitUpdatedOrgBusinessType,
      emitValid,
      setup,
      onOrgBusinessTypeChange,
    };
  },
});
