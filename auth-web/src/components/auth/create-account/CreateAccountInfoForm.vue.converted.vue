import { defineComponent, computed, ref } from "@vue/composition-api";
import { BcolAccountDetails, BcolProfile } from "@/models/bcol";
import { Component, Mixins, Prop, Vue } from "vue-property-decorator";
import { CreateRequestBody, Member, Organization } from "@/models/Organization";
import { mapActions, mapState } from "vuex";
import { Account } from "@/util/constants";
import AccountCreateBasic from "@/components/auth/create-account/AccountCreateBasic.vue";
import AccountCreatePremium from "@/components/auth/create-account/AccountCreatePremium.vue";
import { KCUserProfile } from "sbc-common-components/src/models/KCUserProfile";
import OrgModule from "@/store/modules/org";
import Steppable from "@/components/auth/common/stepper/Steppable.vue";
import { getModule } from "vuex-module-decorators";
export default defineComponent({
  components: {
    AccountCreatePremium,
    AccountCreateBasic,
  },
  props: {},
  setup(_props, ctx) {
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const userProfile = computed(() => ctx.root.$store.state.user.userProfile);
    const currentUser = computed(() => ctx.root.$store.state.user.currentUser);
    const createOrg = () => ctx.root.$store.dispatch("org/createOrg");
    const syncMembership = () => ctx.root.$store.dispatch("org/syncMembership");
    const syncOrganization = () =>
      ctx.root.$store.dispatch("org/syncOrganization");
    const orgStore = ref(getModule(OrgModule, ctx.root.$store));
    const username = ref("");
    const password = ref("");
    const errorMessage = ref<string>("");
    const saving = ref(false);
    const createOrg =
      ref<(requestBody: CreateRequestBody) => Promise<Organization>>(undefined);
    const syncMembership = ref<(orgId: number) => Promise<Member>>(undefined);
    const syncOrganization =
      ref<(orgId: number) => Promise<Organization>>(undefined);
    const currentOrganization = ref<Organization>(undefined);
    const currentUser = ref<KCUserProfile>(undefined);
    const $refs = ref<{
      createAccountInfoForm: HTMLFormElement;
    }>(undefined);
    const teamNameRules = ref([(v) => !!v || "An account name is required"]);
    const isFormValid = (): boolean => {
      return !!username.value && !!password.value;
    };
    const isPremium = () => {
      return currentOrganization.value.orgType === Account.PREMIUM;
    };
    const redirectToNext = (organization?: Organization) => {
      ctx.root.$router.push({ path: `/account/${organization.id}/` });
    };
    return {
      currentOrganization,
      userProfile,
      currentUser,
      createOrg,
      syncMembership,
      syncOrganization,
      orgStore,
      username,
      password,
      errorMessage,
      saving,
      createOrg,
      syncMembership,
      syncOrganization,
      currentOrganization,
      currentUser,
      $refs,
      teamNameRules,
      isFormValid,
      isPremium,
      redirectToNext,
    };
  },
});
