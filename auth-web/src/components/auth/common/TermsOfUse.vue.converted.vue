import {
  defineComponent,
  computed,
  toRefs,
  ref,
  onMounted,
} from "@vue/composition-api";
import { Component, Emit, Prop, Vue } from "vue-property-decorator";
import { mapActions, mapMutations, mapState } from "vuex";
import CommonUtils from "@/util/common-util";
import { TermsOfUseDocument } from "@/models/TermsOfUseDocument";
import { User } from "@/models/user";
import documentService from "@/services/document.services.ts";
export default defineComponent({
  props: { tosType: { default: "termsofuse", type: String } },
  setup(props, ctx) {
    const termsOfUse = computed(() => ctx.root.$store.state.user.termsOfUse);
    const userProfile = computed(() => ctx.root.$store.state.user.userProfile);
    const userHasToAcceptTOS = computed(
      () => ctx.root.$store.state.user.userHasToAcceptTOS
    );
    const getTermsOfUse = () => ctx.root.$store.dispatch("user/getTermsOfUse");
    const { tosType } = toRefs(props);
    const getTermsOfUse =
      ref<(docType?: string) => TermsOfUseDocument>(undefined);
    const termsContent = ref("");
    const userProfile = ref<User>(undefined);
    const userHasToAcceptTOS = ref<boolean>(undefined);
    const hasAcceptedLatestTos = (latestVersionId: string) => {
      const userTOS = userProfile.value?.userTerms?.termsOfUseAcceptedVersion;
      if (!userTOS) {
        return true;
      }
      const currentlyAcceptedTermsVersion =
        CommonUtils.extractAndConvertStringToNumber(userTOS);
      const latestVersionNumber =
        CommonUtils.extractAndConvertStringToNumber(latestVersionId);
      return currentlyAcceptedTermsVersion > latestVersionNumber;
    };
    onMounted(async () => {
      const termsOfService = await getTermsOfUse.value(tosType.value);
      termsContent.value = termsOfService.content;
      const hasLatestTermsAccepted = hasAcceptedLatestTos(
        termsOfService.versionId
      );
      if (!hasLatestTermsAccepted) {
        ctx.emit("tos-version-updated");
      }
    });
    return {
      termsOfUse,
      userProfile,
      userHasToAcceptTOS,
      getTermsOfUse,
      getTermsOfUse,
      termsContent,
      userProfile,
      userHasToAcceptTOS,
      hasAcceptedLatestTos,
    };
  },
});
