import { defineComponent, ref } from "@vue/composition-api";
import { Component, Prop, Vue } from "vue-property-decorator";
import { Pages } from "@/util/constants";
export default defineComponent({
  props: {},
  setup(_props, ctx) {
    const steps = ref([
      {
        number: 1,
        stepTitle: "Get an identity affidavit notarized",
        stepDescription:
          "<p>Visit your local notary or lawyer to have this document notarized. This is to ensure that no one is impersonating you or committing identity theft.</p><p><em>Only account administrators are required to verify their identity with a notary.</em><p>",
        icon: "mdi-scale-balance",
      },
      {
        number: 2,
        stepTitle: "Create a BCeID",
        stepDescription:
          "<p>A username and password that provides secure access to online government services in British Columbia.</p>",
        icon: "mdi-account-circle-outline",
      },
      {
        number: 3,
        stepTitle: "Use a 2-factor mobile or desktop authentication app",
        stepDescription: `<p>Mobile options such as: Google or Microsoft Authenticator<br />
      Desktop options such as: <a href="https://authy.com/" target="_sbc">Authy</a> or 
      <a href="https://chrome.google.com/webstore/detail/gauth-authenticator/ilgcnhelpchnceeipipijaljkblbcobl?hl=en" target="_sbc_google">GAuth</a></p>`,
        icon: "mdi-cellphone-arrow-down",
      },
    ]);
    const goToDownload = () => {
      ctx.root.$router.push(
        `/${Pages.SETUP_ACCOUNT_NON_BCSC}/${Pages.SETUP_ACCOUNT_NON_BCSC_DOWNLOAD}`
      );
      window.scrollTo(0, 0);
    };
    const goBack = () => {
      ctx.root.$router.push(`/${Pages.HOME}`);
      window.scrollTo(0, 0);
    };
    return { steps, goToDownload, goBack };
  },
});
