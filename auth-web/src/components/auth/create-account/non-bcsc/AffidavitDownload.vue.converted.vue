import { defineComponent, computed, ref } from "@vue/composition-api";
import { Component, Vue } from "vue-property-decorator";
import { IdpHint, Pages, SessionStorageKeys } from "@/util/constants";
import AuthModule from "sbc-common-components/src/store/modules/auth";
import CommonUtils from "@/util/common-util";
import ConfigHelper from "@/util/config-helper";
import DocumentService from "@/services/document.services";
import { getModule } from "vuex-module-decorators";
import { mapGetters } from "vuex";
export default defineComponent({
  props: {},
  setup(_props, ctx) {
    const isAuthenticated = computed(
      () => ctx.root.$store.getters["auth/isAuthenticated"]
    );
    const authModule = ref(getModule(AuthModule, ctx.root.$store));
    const isAuthenticated = ref<boolean>(undefined);
    const downloadFailedMsg = ref("Failed download");
    const isDownloadFailed = ref(false);
    const affidavitSize = ref(ConfigHelper.getAffidavitSize() || "");
    const downloadAffidavit = async () => {
      try {
        isDownloadFailed.value = false;
        const downloadData = await DocumentService.getAffidavitPdf();
        CommonUtils.fileDownload(
          downloadData?.data,
          `affidavit.pdf`,
          downloadData?.headers["content-type"]
        );
      } catch (err) {
        console.error(err);
        isDownloadFailed.value = true;
      }
    };
    const redirectToBceId = () => {
      window.location.href = ConfigHelper.getBceIdOsdLink();
    };
    const signinUsingBCeID = () => {
      ctx.root.$router.push(`/${Pages.SIGNIN}/${IdpHint.BCEID}`);
    };
    const continueNext = () => {
      const invToken = ConfigHelper.getFromSession(
        SessionStorageKeys.InvitationToken
      );
      const affidavitNeeded = ConfigHelper.getFromSession(
        SessionStorageKeys.AffidavitNeeded
      );
      if (invToken && affidavitNeeded === "true") {
        ctx.root.$router.push(`/${Pages.SIGNIN}/${IdpHint.BCEID}`);
      } else {
        ctx.root.$router.push(`/${Pages.CREATE_NON_BCSC_ACCOUNT}`);
      }
    };
    const goBack = () => {
      ctx.root.$router.push(
        `/${Pages.SETUP_ACCOUNT_NON_BCSC}/${Pages.SETUP_ACCOUNT_NON_BCSC_INSTRUCTIONS}`
      );
      window.scrollTo(0, 0);
    };
    return {
      isAuthenticated,
      authModule,
      isAuthenticated,
      downloadFailedMsg,
      isDownloadFailed,
      affidavitSize,
      downloadAffidavit,
      redirectToBceId,
      signinUsingBCeID,
      continueNext,
      goBack,
    };
  },
});
