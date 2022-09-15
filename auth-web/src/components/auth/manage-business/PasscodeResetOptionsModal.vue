import { defineComponent, ref } from "@vue/composition-api";
import { Component, Vue } from "vue-property-decorator";
import CommonUtils from "@/util/common-util";
import ModalDialog from "@/components/auth/common/ModalDialog.vue";
export default defineComponent({
  components: {
    ModalDialog,
  },
  props: {},
  setup(_props, ctx) {
    const isResetPasscode = ref<boolean>(false);
    const emailAddress = ref("");
    const confirmedEmailAddress = ref("");
    const emailRules = ref(CommonUtils.emailRules());
    const $refs = ref<{
      passcodeResetEmailForm: HTMLFormElement;
      passcodeResetOptionsDialog: ModalDialog;
    }>(undefined);
    const emailMustMatch = (): string => {
      return emailAddress.value === confirmedEmailAddress.value
        ? ""
        : "Email addresses must match";
    };
    const open = () => {
      ctx.refs.passcodeResetOptionsDialog.open();
    };
    const close = () => {
      ctx.refs.passcodeResetOptionsDialog.close();
    };
    const isFormValid = (): boolean => {
      return ctx.refs.passcodeResetEmailForm?.validate() && !emailMustMatch();
    };
    const confirmPasscodeResetOptions = () => {
      if (isResetPasscode.value) {
        if (isFormValid()) {
          ctx.emit("confirm-passcode-reset-options", emailAddress.value);
        }
      } else {
        ctx.emit("confirm-passcode-reset-options");
      }
    };
    return {
      isResetPasscode,
      emailAddress,
      confirmedEmailAddress,
      emailRules,
      $refs,
      emailMustMatch,
      open,
      close,
      isFormValid,
      confirmPasscodeResetOptions,
    };
  },
});
