import {
  defineComponent,
  toRefs,
  ref,
  watch,
  onBeforeMount,
  PropType,
} from "@vue/composition-api";
import { Component, Emit, Prop, Vue, Watch } from "vue-property-decorator";
import { Address } from "@/models/address";
import BaseAddressForm from "@/components/auth/common/BaseAddressForm.vue";
import { NotaryInformation } from "@/models/notary";
import { addressSchema } from "@/schemas";
export default defineComponent({
  components: {
    BaseAddressForm,
  },
  props: {
    inputNotaryInfo: { type: Object as PropType<NotaryInformation> },
    disabled: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const { inputNotaryInfo, disabled } = toRefs(props);
    const notaryInfo = ref<NotaryInformation>({});
    const isNotaryAddressValid = ref<boolean>(false);
    const notaryAddress = ref<Address>({} as Address);
    const notaryAddressSchema = ref<{}>(addressSchema);
    const $refs = ref<{
      notaryInformationForm: HTMLFormElement;
    }>(undefined);
    const rules = ref({
      notaryName: [(v) => !!v || "Name of Notary is required"],
    });
    const updateNotaryAddress = (val: Address) => {
      notaryInfo.value.address = { ...val };
      return emitNotaryInformation();
    };
    const notaryAddressValidity = (isValid: boolean) => {
      isNotaryAddressValid.value = isValid;
      emitNotaryInformation();
    };
    const updateNotary = async (val, oldVal) => {
      emitNotaryInformation();
    };
    const emitNotaryInformation = () => {
      isFormValid();
      return notaryInfo.value;
    };
    const isFormValid = () => {
      return (
        ctx.refs.notaryInformationForm?.validate() && isNotaryAddressValid.value
      );
    };
    watch(notaryInfo, updateNotary, { deep: true });
    onBeforeMount(() => {
      if (inputNotaryInfo.value) {
        Object.keys(inputNotaryInfo.value)
          .filter((key) => key !== "address")
          .forEach((key) => {
            ctx.root.$set(notaryInfo.value, key, inputNotaryInfo.value?.[key]);
          });
        notaryAddress.value = { ...inputNotaryInfo.value?.address };
      }
    });
    return {
      notaryInfo,
      isNotaryAddressValid,
      notaryAddress,
      notaryAddressSchema,
      $refs,
      rules,
      updateNotaryAddress,
      notaryAddressValidity,
      updateNotary,
      emitNotaryInformation,
      isFormValid,
    };
  },
});
