import { defineComponent, toRefs, ref, PropType } from "@vue/composition-api";
import { AddUserBody, Member, Organization } from "@/models/Organization";
import { Component, Emit, Prop, Vue } from "vue-property-decorator";
import { mapActions, mapMutations, mapState } from "vuex";
import CommonUtils from "@/util/common-util";
import ModalDialog from "@/components/auth/common/ModalDialog.vue";
import PasswordRequirementAlert from "@/components/auth/common/PasswordRequirementAlert.vue";
import { User } from "@/models/user";
export default defineComponent({
  components: {
    ModalDialog,
    PasswordRequirementAlert,
  },
  props: { user: { type: Object as PropType<User> } },
  setup(props, ctx) {
    const resetPassword = () => ctx.root.$store.dispatch("org/resetPassword");
    const { user } = toRefs(props);
    const loading = ref(false);
    const resetPassword = ref<(AddUserBody) => Promise<void>>(undefined);
    const password = ref("");
    const inputHints = ref({
      username: "Minimum 8 characters",
      password: "See requirements above",
    });
    const $refs = ref<{
      form: HTMLFormElement;
      passwordResetDialog: PasswordReset;
    }>(undefined);
    const users = ref<AddUserBody[]>([]);
    const passwordRules = ref([
      (value) => CommonUtils.validatePasswordRules(value) || `Invalid Password`,
    ]);
    const isFormValid = (): boolean => {
      let isValid: boolean = false;
      if (password.value) {
        isValid = CommonUtils.validatePasswordRules(password.value);
      }
      return isValid;
    };
    const resetForm = () => {
      ctx.refs.form?.reset();
    };
    const cancel = () => {
      resetForm();
    };
    const changePassword = async () => {
      if (isFormValid()) {
        loading.value = true;
        try {
          await resetPassword.value({
            username: user.value.username,
            password: password.value,
          });
        } catch (error) {
          loading.value = false;
          ctx.emit("reset-error");
          return;
        }
        resetForm();
        ctx.emit("reset-complete");
        loading.value = false;
      }
    };
    return {
      resetPassword,
      loading,
      resetPassword,
      password,
      inputHints,
      $refs,
      users,
      passwordRules,
      isFormValid,
      resetForm,
      cancel,
      changePassword,
    };
  },
});
