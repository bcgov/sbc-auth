import {
  defineComponent,
  toRefs,
  ref,
  onMounted,
  PropType,
} from "@vue/composition-api";
import { Address, BaseAddressModel } from "@/models/address";
import { Component, Emit, Prop, Vue } from "vue-property-decorator";
import BaseAddress from "sbc-common-components/src/components/BaseAddress.vue";
import CommonUtils from "@/util/common-util";
export default defineComponent({
  components: {
    BaseAddress,
  },
  props: {
    editing: { default: true, type: Boolean },
    schema: { default: {}, type: Object as PropType<any> },
    address: {
      default: () => ({} as Address),
      type: Object as PropType<Address>,
    },
  },
  setup(props, ctx) {
    const { editing, schema, address } = toRefs(props);
    const inputaddress = ref<BaseAddressModel>({} as BaseAddressModel);
    const emitUpdateAddress = (iaddress): Address => {
      const address = CommonUtils.convertAddressForAuth(iaddress);
      return address;
    };
    const emitAddressValidity = (isValid) => {
      return isValid;
    };
    onMounted(() => {
      if (address.value) {
        inputaddress.value = CommonUtils.convertAddressForComponent(
          address.value
        );
        emitUpdateAddress(inputaddress.value);
      }
    });
    return { inputaddress, emitUpdateAddress, emitAddressValidity };
  },
});
