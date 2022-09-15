import { defineComponent, toRefs, ref, PropType } from "@vue/composition-api";
import { Component, Emit, Prop, Vue } from "vue-property-decorator";
import BaseAddressForm from "@/components/auth/common/BaseAddressForm.vue";
import { addressSchema } from "@/schemas";
export default defineComponent({
  components: {
    BaseAddressForm,
  },
  props: {
    baseAddress: { default: null, type: Object as PropType<any> },
    viewOnlyMode: { default: true, type: Boolean },
  },
  setup(props, ctx) {
    const { baseAddress, viewOnlyMode } = toRefs(props);
    const baseAddressSchema = ref<{}>(addressSchema);
    const $refs = ref<{
      mailingAddress: HTMLFormElement;
    }>(undefined);
    const updateAddress = (address) => {
      return address;
    };
    const checkBaseAddressValidity = (isValid) => {
      return isValid;
    };
    const triggerValidate = (): boolean => {
      return ctx.refs.mailingAddress?.$refs.baseAddress?.$refs.addressForm?.validate();
    };
    return {
      baseAddressSchema,
      $refs,
      updateAddress,
      checkBaseAddressValidity,
      triggerValidate,
    };
  },
});
