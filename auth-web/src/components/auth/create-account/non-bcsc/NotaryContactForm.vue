import {
  defineComponent,
  toRefs,
  ref,
  watch,
  onMounted,
  PropType,
} from "@vue/composition-api";
import { Component, Emit, Prop, Vue, Watch } from "vue-property-decorator";
import CommonUtils from "@/util/common-util";
import { NotaryContact } from "@/models/notary";
export default defineComponent({
  props: {
    inputNotaryContact: { type: Object as PropType<NotaryContact> },
    disabled: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const { inputNotaryContact, disabled } = toRefs(props);
    const notaryContact = ref<NotaryContact>({});
    const $refs = ref<{
      notaryContactForm: HTMLFormElement;
    }>(undefined);
    const rules = ref({
      email: [
        (val) => {
          if (val) {
            return !!CommonUtils.validateEmailFormat(val) || "Email is invalid";
          }
          return true;
        },
      ],
    });
    const updateContact = async (val, oldVal) => {
      emitNotaryContact();
    };
    const emitNotaryContact = () => {
      isFormValid();
      return notaryContact.value;
    };
    const isFormValid = () => {
      return ctx.refs.notaryContactForm.validate();
    };
    watch(notaryContact, updateContact, { deep: true });
    onMounted(() => {
      if (inputNotaryContact.value) {
        Object.keys(inputNotaryContact.value).forEach((key) => {
          ctx.root.$set(
            notaryContact.value,
            key,
            inputNotaryContact.value?.[key]
          );
        });
      }
      ctx.root.$nextTick(() => {
        isFormValid();
      });
    });
    return {
      notaryContact,
      $refs,
      rules,
      updateContact,
      emitNotaryContact,
      isFormValid,
    };
  },
});
