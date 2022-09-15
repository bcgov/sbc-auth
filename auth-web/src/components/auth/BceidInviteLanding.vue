import { defineComponent, toRefs, ref, onMounted } from "@vue/composition-api";
import { Component, Mixins, Prop, Watch } from "vue-property-decorator";
import ConfigHelper from "@/util/config-helper";
import CreateUserProfileForm from "@/components/auth/CreateUserProfileForm.vue";
import InterimLanding from "@/components/auth/common/InterimLanding.vue";
import { SessionStorageKeys } from "@/util/constants";
import Vue from "vue";
export default defineComponent({
  components: {
    CreateUserProfileForm,
    InterimLanding,
  },
  props: { token: { type: String }, orgName: { default: "", type: String } },
  setup(props, ctx) {
    const { token, orgName } = toRefs(props);
    const isLoading = ref(true);
    const inviteError = ref(false);
    const steps = ref([
      {
        number: 1,
        stepTitle: "Register or use an existing BCeID account",
        stepDescription:
          "<p>A BCeID account provides secure access to online government services in British Columbia.\n" +
          "You can register a new BCeID or use an existing BCeID account to log into BC Registries.</p>",
        icon: "mdi-account-plus-outline",
      },
      {
        number: 2,
        stepTitle: "Use a 2-factor mobile or desktop authentication app",
        stepDescription: `<p>Secure your account using a 2-factor authentication app with your BCeID when you log in. 
      Download a 2-factor authentication app to your smartphone such as FreeOTP, Google Authenticator or 
      Microsoft Authenticator or Desktop options such as: 
      <a href="https://authy.com/" target="_sbc">Authy</a> or 
      <a href="https://chrome.google.com/webstore/detail/gauth-authenticator/ilgcnhelpchnceeipipijaljkblbcobl?hl=en" target="_sbc_google">GAuth</a>.</p>`,
        icon: "mdi-two-factor-authentication",
      },
    ]);
    const registerForBceid = () => {
      setStorage();
      window.location.href = ConfigHelper.getBceIdOsdLink();
    };
    const loginWithBceid = () => {
      setStorage();
      ctx.root.$router.push("/signin/bceid/");
    };
    const setStorage = () => {
      ConfigHelper.addToSession(
        SessionStorageKeys.InvitationToken,
        token.value
      );
    };
    const showErrorOccured = () => {
      inviteError.value = true;
    };
    onMounted(async () => {
      isLoading.value = false;
    });
    return {
      isLoading,
      inviteError,
      steps,
      registerForBceid,
      loginWithBceid,
      setStorage,
      showErrorOccured,
    };
  },
});
