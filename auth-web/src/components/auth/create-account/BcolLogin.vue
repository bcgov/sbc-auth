import {
  defineComponent,
  computed,
  toRefs,
  ref,
  watch,
  onMounted,
} from "@vue/composition-api";
import { BcolAccountDetails, BcolProfile } from "@/models/bcol";
import { Component, Emit, Prop, Vue, Watch } from "vue-property-decorator";
import { mapActions, mapState } from "vuex";
export default defineComponent({
  name: "BcolLogin",
  props: {
    hideLinkBtn: { default: false, type: Boolean },
    defaultUserId: { type: String },
  },
  setup(props, ctx) {
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const syncMembership = () => ctx.root.$store.dispatch("org/syncMembership");
    const syncOrganization = () =>
      ctx.root.$store.dispatch("org/syncOrganization");
    const validateBcolAccount = () =>
      ctx.root.$store.dispatch("org/validateBcolAccount");
    const { hideLinkBtn, defaultUserId } = toRefs(props);
    const username = ref<string>("");
    const password = ref<string>("");
    const errorMessage = ref<string>("");
    const isLoading = ref<boolean>(false);
    const validateBcolAccount =
      ref<(bcolProfile: BcolProfile) => Promise<BcolAccountDetails>>(undefined);
    const usernameRules = ref([(v) => !!v.trim() || "Username is required"]);
    const passwordRules = ref([(value) => !!value || "Password is required"]);
    const $refs = ref<{
      form: HTMLFormElement;
    }>(undefined);
    const onPasswordChange = () => {
      emitBcolInfo();
    };
    const onUsernameChange = () => {
      emitBcolInfo();
    };
    const isFormValid = (): boolean => {
      return !!username.value && !!password.value;
    };
    const linkAccounts = async () => {
      isLoading.value = true;
      errorMessage.value = "";
      if (isFormValid()) {
        const bcolProfile: BcolProfile = {
          userId: username.value,
          password: password.value,
        };
        try {
          const bcolAccountDetails = await validateBcolAccount.value(
            bcolProfile
          );
          isLoading.value = false;
          if (bcolAccountDetails) {
            ctx.emit("account-link-successful", {
              bcolProfile,
              bcolAccountDetails,
            });
            resetForm();
          }
        } catch (err) {
          isLoading.value = false;
          switch (err.response.status) {
            case 409:
              errorMessage.value = err.response.data.message;
              break;
            case 400:
              errorMessage.value = err.response.data.message;
              break;
            default:
              errorMessage.value =
                "An error occurred while attempting to create your account.";
          }
        }
      }
    };
    const resetForm = () => {
      password.value = errorMessage.value = "";
      ctx.refs.form.resetValidation();
    };
    const emitBcolInfo = async () => {
      const bcolInfo: BcolProfile = {
        userId: username.value,
        password: password.value,
      };
      return bcolInfo;
    };
    watch(password, onPasswordChange);
    watch(username, onUsernameChange);
    onMounted(async () => {
      username.value = defaultUserId.value;
      password.value = "";
    });
    return {
      currentOrganization,
      syncMembership,
      syncOrganization,
      validateBcolAccount,
      username,
      password,
      errorMessage,
      isLoading,
      validateBcolAccount,
      usernameRules,
      passwordRules,
      $refs,
      onPasswordChange,
      onUsernameChange,
      isFormValid,
      linkAccounts,
      resetForm,
      emitBcolInfo,
    };
  },
});
