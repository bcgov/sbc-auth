import {
  defineComponent,
  toRefs,
  ref,
  computed,
  onMounted,
} from "@vue/composition-api";
import {
  AccessType,
  Account,
  LoginSource,
  SessionStorageKeys,
} from "@/util/constants";
import { Component, Mixins, Prop } from "vue-property-decorator";
import ConfigHelper from "@/util/config-helper";
import ConfirmCancelButton from "@/components/auth/common/ConfirmCancelButton.vue";
import { KCUserProfile } from "sbc-common-components/src/models/KCUserProfile";
import { Organization } from "@/models/Organization";
import Steppable from "@/components/auth/common/stepper/Steppable.vue";
import { namespace } from "vuex-class";
const OrgModule = namespace("org");
const UserModule = namespace("user");
export default defineComponent({
  components: {
    ConfirmCancelButton,
  },
  props: { cancelUrl: { type: String } },
  setup(props, ctx) {
    const { cancelUrl } = toRefs(props);
    const ACCOUNT_TYPE = ref(Account);
    const selectedAccountType = ref("");
    const canContinue = computed(() => {
      return selectedAccountType.value;
    });
    const selectAccountType = (accountType) => {
      setSelectedAccountType(accountType);
      setCurrentOrganizationType(accountType);
      selectedAccountType.value = accountType;
    };
    const getOrgAccessType = () => {
      let isBceidUser = currentUser?.loginSource === LoginSource.BCEID;
      let isExtraProvice = JSON.parse(
        ConfigHelper.getFromSession(
          SessionStorageKeys.ExtraProvincialUser || "{}"
        )
      );
      const isGovNAccount = !!JSON.parse(
        ConfigHelper.getFromSession(SessionStorageKeys.GOVN_USER || "false")
      );
      if (isGovNAccount) {
        return AccessType.GOVN;
      }
      return isBceidUser
        ? isExtraProvice
          ? AccessType.EXTRA_PROVINCIAL
          : AccessType.REGULAR_BCEID
        : AccessType.REGULAR;
    };
    const goNext = () => {
      stepForward(selectedAccountType.value === ACCOUNT_TYPE.value.PREMIUM);
    };
    const goBack = () => {
      stepBack();
    };
    const cancel = () => {
      ctx.root.$router.push({ path: "/home" });
    };
    onMounted(async () => {
      if (!currentOrganization) {
        setCurrentOrganization({ name: "" });
      } else {
        selectAccountType(currentOrganization.orgType);
      }
      if (!currentOrganization && resetAccountTypeOnSetupAccount) {
        selectAccountType(undefined);
        setResetAccountTypeOnSetupAccount(false);
      }
      if (!currentOrganizationType && isCurrentProductsPremiumOnly) {
        selectAccountType(ACCOUNT_TYPE.value.PREMIUM);
      } else {
        selectedAccountType.value =
          currentOrganizationType === ACCOUNT_TYPE.value.UNLINKED_PREMIUM
            ? ACCOUNT_TYPE.value.PREMIUM
            : currentOrganizationType;
      }
      setAccessType(getOrgAccessType());
      const accessType = getOrgAccessType();
      setCurrentOrganization({
        ...currentOrganization,
        ...{ accessType: accessType },
      });
      ConfigHelper.removeFromSession("CURRENT_ACCOUNT");
    });
    return {
      ACCOUNT_TYPE,
      selectedAccountType,
      canContinue,
      selectAccountType,
      getOrgAccessType,
      goNext,
      goBack,
      cancel,
    };
  },
});
