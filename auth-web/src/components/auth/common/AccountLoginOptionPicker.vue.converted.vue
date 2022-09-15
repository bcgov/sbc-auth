import {
  defineComponent,
  computed,
  ref,
  onMounted,
} from "@vue/composition-api";
import { Component, Emit, Mixins } from "vue-property-decorator";
import { LDFlags, LoginSource } from "@/util/constants";
import { mapActions, mapMutations, mapState } from "vuex";
import AccountChangeMixin from "@/components/auth/mixins/AccountChangeMixin.vue";
import AccountMixin from "@/components/auth/mixins/AccountMixin.vue";
import LaunchDarklyService from "sbc-common-components/src/services/launchdarkly.services";
import LearnMoreBCEID from "@/components/auth/common/LearnMoreBCEID.vue";
import LearnMoreBCSC from "@/components/auth/common/LearnMoreBCSC.vue";
import { Organization } from "@/models/Organization";
export default defineComponent({
  components: {
    LearnMoreBCEID,
    LearnMoreBCSC,
  },
  props: {},
  setup(_props, ctx) {
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const memberLoginOption = computed(
      () => ctx.root.$store.state.org.memberLoginOption
    );
    const syncMemberLoginOption = () =>
      ctx.root.$store.dispatch("org/syncMemberLoginOption");
    const updateLoginOption = () =>
      ctx.root.$store.dispatch("org/updateLoginOption");
    const btnLabel = ref("Save");
    const memberLoginOption = ref<LoginSource>(undefined);
    const syncMemberLoginOption =
      ref<(currentAccount: number) => string>(undefined);
    const syncOrganization =
      ref<(currentAccount: number) => Promise<Organization>>(undefined);
    const updateLoginOption =
      ref<(loginType: string) => Promise<string>>(undefined);
    const errorMessage = ref<string>("");
    const authType = ref(LoginSource.BCSC);
    const authOptions = ref([
      {
        type: LoginSource.BCSC,
        title: ctx.root.$t("bCSCLoginOptionTitle"),
        description: ctx.root.$t("bCSCLoginOptionDescription"),
        icon: "mdi-account-card-details-outline",
      },
      {
        type: LoginSource.BCEID,
        title: ctx.root.$t("bCeIDLoginOptionTitle"),
        description: ctx.root.$t("bCeIDLoginOptionDescription"),
        icon: "mdi-two-factor-authentication",
      },
    ]);
    const $refs = ref<{
      bcscLearnMoreDialog: LearnMoreBCSC;
      bceidLearnMoreDialog: LearnMoreBCEID;
    }>(undefined);
    const showLearnMore = computed((): boolean => {
      return LaunchDarklyService.getFlag(LDFlags.AuthLearnMore) || false;
    });
    const loginSourceEnum = computed(() => {
      return LoginSource;
    });
    const selectAuthType = (authType: LoginSource) => {
      authType.value = authType;
      return authType;
    };
    const selectLearnMore = (authType: LoginSource) => {
      switch (authType) {
        case LoginSource.BCSC:
          window.open(
            "https://www2.gov.bc.ca/gov/content/governments/government-id/bcservicescardapp/setup",
            "_blank"
          );
          break;
        case LoginSource.BCEID:
          ctx.refs.bceidLearnMoreDialog.open();
          break;
        default:
      }
    };
    onMounted(async () => {
      if (!memberLoginOption.value) {
        await syncMemberLoginOption.value(getAccountFromSession().id);
      }
      authType.value = memberLoginOption.value
        ? memberLoginOption.value
        : authType.value;
    });
    return {
      currentOrganization,
      memberLoginOption,
      syncMemberLoginOption,
      updateLoginOption,
      btnLabel,
      memberLoginOption,
      syncMemberLoginOption,
      syncOrganization,
      updateLoginOption,
      errorMessage,
      authType,
      authOptions,
      $refs,
      showLearnMore,
      loginSourceEnum,
      selectAuthType,
      selectLearnMore,
    };
  },
});
