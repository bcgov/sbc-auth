import { defineComponent, toRefs, ref, onMounted } from "@vue/composition-api";
import { Component, Mixins, Prop, Vue } from "vue-property-decorator";
import CommonUtils from "@/util/common-util";
import ConfigHelper from "@/util/config-helper";
import ModalDialog from "@/components/auth/common/ModalDialog.vue";
import NextPageMixin from "@/components/auth/mixins/NextPageMixin.vue";
import { Organization } from "@/models/Organization";
import { UserProfileRequestBody } from "@/models/user";
import UserService from "@/services/user.services";
export default defineComponent({
  components: {
    ModalDialog,
  },
  props: { token: { type: String } },
  setup(props, ctx) {
    const { token } = toRefs(props);
    const username = ref("");
    const password = ref("");
    const confirmPassword = ref("");
    const isLoading = ref(false);
    const dialogTitle = ref("");
    const dialogText = ref("");
    const passwordRuleValid = ref(false);
    const inputHints = ref({
      username: "Minimum 8 characters",
      password: `Minimum of 8 characters and includes the following:`,
      confirmPassword: "Minimum of 8 characters",
    });
    const $refs = ref<{
      form: HTMLFormElement;
      errorDialog: ModalDialog;
    }>(undefined);
    const usernameRules = ref([
      (v) => !!v.trim() || "Username is required",
      (v) => v.trim().length >= 8 || inputHints.value.username,
    ]);
    const passwordRules = ref([
      (value) => !!value || "Password is required",
      (value) => validatePassword(value) || inputHints.value.password,
    ]);
    const passwordMustMatch = (): string => {
      return password.value === confirmPassword.value
        ? ""
        : "Passwords must match";
    };
    const isFormValid = (): boolean => {
      return ctx.refs.form && ctx.refs.form.validate() && !passwordMustMatch();
    };
    const nextStep = async () => {
      if (isFormValid()) {
        isLoading.value = true;
        const requestBody: UserProfileRequestBody = {
          username: username.value.trim().toLowerCase(),
          password: password.value,
        };
        try {
          const response = await UserService.createUserProfile(
            token.value,
            requestBody
          );
          if (response?.data?.users?.length) {
            redirectToSignin();
          }
        } catch (error) {
          isLoading.value = false;
          if (error?.response?.data?.code) {
            switch (error.response.data.code) {
              case "FAILED_ADDING_USER_IN_KEYCLOAK":
                showErrorModal("Failed to add the user, please try again");
                break;
              case 409:
                showErrorModal(
                  "The username has already been taken.Please try another user name."
                );
                break;
              default:
                showErrorModal();
            }
          } else {
            ctx.emit("show-error-message");
          }
        }
      }
    };
    const redirectToSignin = () => {
      let redirectUrl =
        ConfigHelper.getSelfURL() + "/confirmtoken/" + token.value;
      ctx.root.$router.push("/signin/bcros/" + encodeURIComponent(redirectUrl));
    };
    const cancel = () => {
      ctx.root.$router.push("/signin/bcros/");
    };
    const validatePassword = (value) => {
      passwordRuleValid.value = CommonUtils.validatePasswordRules(value);
      return passwordRuleValid.value;
    };
    const close = () => {
      ctx.refs.errorDialog.close();
    };
    const showErrorModal = (msg?) => {
      dialogTitle.value = "An error has occured";
      dialogText.value =
        msg ||
        "Something went wrong while attempting to create this profile. Please try again later.";
      ctx.refs.errorDialog.open();
    };
    onMounted(async () => {});
    return {
      username,
      password,
      confirmPassword,
      isLoading,
      dialogTitle,
      dialogText,
      passwordRuleValid,
      inputHints,
      $refs,
      usernameRules,
      passwordRules,
      passwordMustMatch,
      isFormValid,
      nextStep,
      redirectToSignin,
      cancel,
      validatePassword,
      close,
      showErrorModal,
    };
  },
});
