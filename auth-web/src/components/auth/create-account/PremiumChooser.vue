import {
  defineComponent,
  computed,
  toRefs,
  ref,
  onMounted,
} from "@vue/composition-api";
import { Component, Mixins, Prop } from "vue-property-decorator";
import { mapActions, mapMutations, mapState } from "vuex";
import { Account } from "@/util/constants";
import AccountCreateBasic from "@/components/auth/create-account/AccountCreateBasic.vue";
import AccountCreatePremium from "@/components/auth/create-account/AccountCreatePremium.vue";
import ConfirmCancelButton from "@/components/auth/common/ConfirmCancelButton.vue";
import { Organization } from "@/models/Organization";
import Steppable from "@/components/auth/common/stepper/Steppable.vue";
import UserProfileForm from "@/components/auth/create-account/UserProfileForm.vue";
import Vue from "vue";
export default defineComponent({
  components: {
    AccountCreateBasic,
    ConfirmCancelButton,
  },
  props: {
    cancelUrl: { type: String },
    readOnly: { default: false, type: String },
  },
  setup(props, ctx) {
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const currentOrganizationType = computed(
      () => ctx.root.$store.state.org.currentOrganizationType
    );
    const syncMembership = () => ctx.root.$store.dispatch("org/syncMembership");
    const syncOrganization = () =>
      ctx.root.$store.dispatch("org/syncOrganization");
    const resetAccountWhileSwitchingPremium = () =>
      ctx.root.$store.dispatch("org/resetAccountWhileSwitchingPremium");
    const { cancelUrl, readOnly } = toRefs(props);
    const currentOrganizationType = ref<string>(undefined);
    const currentOrganization = ref<Organization>(undefined);
    const isBcolSelected = ref(null);
    const currentComponent = ref(null);
    const saving = ref(false);
    const errorMessage = ref<string>("");
    const setCurrentOrganizationType =
      ref<(orgType: string) => void>(undefined);
    const syncOrganization =
      ref<(orgId: number) => Promise<Organization>>(undefined);
    const resetAccountWhileSwitchingPremium = ref<() => void>(undefined);
    const learnMoreDialog = ref<boolean>(false);
    const $refs = ref<{
      activeComponent: AccountCreatePremium | AccountCreateBasic;
    }>(undefined);
    const loadComponent = (isReset?) => {
      if (isReset) {
        resetAccountWhileSwitchingPremium.value();
      }
      if (isBcolSelected.value === "yes") {
        setCurrentOrganizationType.value(Account.PREMIUM);
        currentComponent.value = AccountCreatePremium;
      } else if (isBcolSelected.value === "no") {
        setCurrentOrganizationType.value(Account.UNLINKED_PREMIUM);
        currentComponent.value = AccountCreateBasic;
      } else {
        currentComponent.value = null;
      }
    };
    const cancel = () => {
      if (stepBack) {
        stepBack();
      } else {
        ctx.root.$router.push({ path: "/home" });
      }
    };
    const closeLearnMore = () => {
      learnMoreDialog.value = false;
    };
    onMounted(() => {
      isBcolSelected.value = readOnly.value ? "no" : null;
      isBcolSelected.value =
        currentOrganizationType.value === Account.PREMIUM &&
        currentOrganization.value?.bcolAccountDetails
          ? "yes"
          : isBcolSelected.value;
      isBcolSelected.value =
        currentOrganizationType.value === Account.UNLINKED_PREMIUM &&
        currentOrganization.value?.name
          ? "no"
          : isBcolSelected.value;
      loadComponent(false);
    });
    return {
      currentOrganization,
      currentOrganizationType,
      syncMembership,
      syncOrganization,
      resetAccountWhileSwitchingPremium,
      currentOrganizationType,
      currentOrganization,
      isBcolSelected,
      currentComponent,
      saving,
      errorMessage,
      setCurrentOrganizationType,
      syncOrganization,
      resetAccountWhileSwitchingPremium,
      learnMoreDialog,
      $refs,
      loadComponent,
      cancel,
      closeLearnMore,
    };
  },
});
