import {
  defineComponent,
  computed,
  toRefs,
  ref,
  onMounted,
} from "@vue/composition-api";
import {
  AccessType,
  Account,
  LDFlags,
  LoginSource,
  Pages,
  Role,
} from "@/util/constants";
import { Component, Emit, Mixins, Prop, Vue } from "vue-property-decorator";
import { Member, Organization } from "@/models/Organization";
import { User, UserProfileData } from "@/models/user";
import { mapActions, mapMutations, mapState } from "vuex";
import CommonUtils from "@/util/common-util";
import ConfirmCancelButton from "@/components/auth/common/ConfirmCancelButton.vue";
import { Contact } from "@/models/contact";
import { KCUserProfile } from "sbc-common-components/src/models/KCUserProfile";
import LaunchDarklyService from "sbc-common-components/src/services/launchdarkly.services";
import ModalDialog from "@/components/auth/common/ModalDialog.vue";
import NextPageMixin from "@/components/auth/mixins/NextPageMixin.vue";
import Steppable from "@/components/auth/common/stepper/Steppable.vue";
import UserService from "@/services/user.services";
import { appendAccountId } from "sbc-common-components/src/util/common-util";
import configHelper from "@/util/config-helper";
import { mask } from "vue-the-mask";
export default defineComponent({
  components: {
    ModalDialog,
    ConfirmCancelButton,
  },
  directives: {
    mask,
  },
  props: {
    isAffidavitUpload: { default: false, type: Boolean },
    token: { type: String },
    isStepperView: { default: false, type: Boolean },
    stepperSource: { default: AccessType.REGULAR, type: String },
    clearForm: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const userProfileData = computed(
      () => ctx.root.$store.state.user.userProfileData
    );
    const createUserContact = () =>
      ctx.root.$store.dispatch("user/createUserContact");
    const updateUserContact = () =>
      ctx.root.$store.dispatch("user/updateUserContact");
    const getUserProfile = () =>
      ctx.root.$store.dispatch("user/getUserProfile");
    const createAffidavit = () =>
      ctx.root.$store.dispatch("user/createAffidavit");
    const updateUserFirstAndLastName = () =>
      ctx.root.$store.dispatch("user/updateUserFirstAndLastName");
    const syncMembership = () => ctx.root.$store.dispatch("org/syncMembership");
    const syncOrganization = () =>
      ctx.root.$store.dispatch("org/syncOrganization");
    const {
      isAffidavitUpload,
      token,
      isStepperView,
      stepperSource,
      clearForm,
    } = toRefs(props);
    const createUserContact = ref<(contact?: Contact) => Contact>(undefined);
    const updateUserContact = ref<(contact?: Contact) => Contact>(undefined);
    const getUserProfile = ref<(identifer: string) => User>(undefined);
    const updateUserFirstAndLastName = ref<(user?: User) => Contact>(undefined);
    const setUserProfileData =
      ref<(userProfile: UserProfileData | undefined) => void>(undefined);
    const setUserProfile =
      ref<(userProfile: User | undefined) => void>(undefined);
    const createAffidavit = ref<() => User>(undefined);
    const firstName = ref("");
    const lastName = ref("");
    const emailAddress = ref("");
    const confirmedEmailAddress = ref("");
    const phoneNumber = ref("");
    const extension = ref("");
    const formError = ref("");
    const editing = ref(false);
    const deactivateProfileDialog = ref(false);
    const isDeactivating = ref(false);
    const currentOrganization = ref<Organization>(undefined);
    const userProfileData = ref<UserProfileData>(undefined);
    const syncMembership = ref<(orgId: number) => Promise<Member>>(undefined);
    const syncOrganization =
      ref<(orgId: number) => Promise<Organization>>(undefined);
    const ACCOUNT_TYPE = ref(Account);
    const isTester = ref<boolean>(false);
    const isReseting = ref(false);
    const currentUser = ref<KCUserProfile>(undefined);
    const $refs = ref<{
      deactivateUserConfirmationDialog: ModalDialog;
      deactivateUserFailureDialog: ModalDialog;
      resetDialog: ModalDialog;
      resetFailureDialog: ModalDialog;
      form: HTMLFormElement;
    }>(undefined);
    const emailRules = ref([
      (v) => !!v || "Email address is required",
      (v) => {
        const pattern =
          /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return pattern.test(v) || "Valid email is required";
      },
    ]);
    const phoneRules = ref([
      (v) =>
        !v || v.length === 0 || v.length === 14 || "Phone number is invalid",
    ]);
    const extensionRules = ref([
      (v) => !v || v.length >= 0 || v.length <= 4 || "Extension is invalid",
    ]);
    const firstNameRules = ref([(v) => !!v || "First Name is Required"]);
    const lastNameRules = ref([(v) => !!v || "Last Name is Required"]);
    const isInEditNameMode = computed(() => {
      return (
        isAffidavitUpload.value ||
        token.value ||
        (isStepperView.value &&
          stepperSource.value === AccessType.EXTRA_PROVINCIAL)
      );
    });
    const isBCEIDUser = computed((): boolean => {
      return currentUser.value?.loginSource === LoginSource.BCEID;
    });
    const enablePaymentMethodSelectorStep = computed((): boolean => {
      return (
        LaunchDarklyService.getFlag(LDFlags.PaymentTypeAccountCreation) || false
      );
    });
    const emailMustMatch = (): string => {
      return emailAddress.value === confirmedEmailAddress.value
        ? ""
        : "Email addresses must match";
    };
    const isFormValid = (): boolean => {
      return (
        ctx.refs.form &&
        ctx.refs.form.validate() &&
        confirmedEmailAddress.value === emailAddress.value
      );
    };
    const save = async () => {
      if (isFormValid()) {
        const user: User = {
          firstname: firstName.value.trim(),
          lastname: lastName.value.trim(),
        };
        const contact = {
          email: emailAddress.value.toLowerCase(),
          phone: phoneNumber.value,
          phoneExtension: extension.value,
        };
        if (isBCEIDUser.value) {
          await updateUserFirstAndLastName.value(user);
        }
        await saveOrUpdateContact(contact);
        await getUserProfile.value("@me");
        if (isAffidavitUpload.value) {
          ctx.emit("emit-admin-profile-complete");
          return;
        }
        if (token.value) {
          ctx.root.$router.push("/confirmtoken/" + token.value);
          return;
        }
        redirectToNext();
      }
    };
    const next = () => {
      const userProfile = {
        firstname: firstName.value.trim(),
        lastname: lastName.value.trim(),
        email: emailAddress.value.toLowerCase(),
        phone: phoneNumber.value,
        phoneExtension: extension.value,
      };
      setUserProfileData.value(userProfile);
      if (enablePaymentMethodSelectorStep.value) {
        stepForward();
      } else {
        createAccount();
      }
    };
    const createAccount = () => {};
    const saveOrUpdateContact = async (contact: Contact) => {
      if (editing.value) {
        await updateUserContact.value(contact);
      } else {
        await createUserContact.value(contact);
      }
    };
    const redirectToNext = () => {
      if (CommonUtils.isUrl(getNextPageUrl())) {
        window.location.assign(appendAccountId(getNextPageUrl()));
      } else {
        ctx.root.$router.push(getNextPageUrl());
      }
    };
    const cancel = () => {
      if (isStepperView.value) {
        ctx.root.$router.push("/");
      } else {
        navigateBack();
      }
    };
    const navigateBack = (): void => {
      if (currentOrganization.value) {
        window.location.assign(configHelper.getBcrosDashboardURL());
      } else {
        ctx.root.$router.push("/home");
      }
    };
    const goBack = () => {
      if (isAffidavitUpload.value) {
        ctx.emit("emit-admin-profile-previous-step");
      } else {
        stepBack(
          currentOrganization.value!.orgType === ACCOUNT_TYPE.value.PREMIUM
        );
      }
    };
    const deactivate = async (): Promise<void> => {
      try {
        isDeactivating.value = true;
        await UserService.deactivateUser();
        const redirectUri = encodeURIComponent(
          `${configHelper.getSelfURL()}/profiledeactivated`
        );
        ctx.root.$router.push(`/${Pages.SIGNOUT}/${redirectUri}`);
      } catch (exception) {
        ctx.refs.deactivateUserFailureDialog.open();
      } finally {
        isDeactivating.value = false;
      }
    };
    const cancelConfirmDeactivate = () => {
      ctx.refs.deactivateUserConfirmationDialog.close();
    };
    const reset = async (): Promise<void> => {
      try {
        isReseting.value = true;
        await UserService.resetUser();
        const redirectUri = encodeURIComponent(
          `${configHelper.getSelfURL()}/profiledeactivated`
        );
        ctx.root.$router.push(`/${Pages.SIGNOUT}/${redirectUri}`);
      } catch (exception) {
        ctx.refs.resetFailureDialog.open();
      } finally {
        isReseting.value = false;
      }
    };
    const cancelConfirmReset = () => {
      ctx.refs.resetDialog.close();
    };
    onMounted(async () => {
      if (!userProfile) {
        await getUserProfile.value("@me");
      }
      let user: any = {};
      if (!clearForm.value) {
        if (userProfileData.value) {
          user = userProfileData.value;
        } else {
          user = { ...userProfile };
          user.email = userContact?.email;
          user.phone = userContact?.phone;
          user.phoneExtension = userContact?.phoneExtension;
        }
      } else {
        user = userProfileData.value;
      }
      firstName.value = user?.firstname || "";
      lastName.value = user?.lastname || "";
      emailAddress.value = user?.email || "";
      emailAddress.value = confirmedEmailAddress.value = user?.email || "";
      phoneNumber.value = user?.phone || "";
      extension.value = user?.phoneExtension || "";
      if (userContact) {
        editing.value = true;
      }
      if (configHelper.getAuthResetAPIUrl()) {
        isTester.value = currentUser.value?.roles?.includes(Role.Tester);
      }
    });
    return {
      currentOrganization,
      userProfileData,
      createUserContact,
      updateUserContact,
      getUserProfile,
      createAffidavit,
      updateUserFirstAndLastName,
      syncMembership,
      syncOrganization,
      createUserContact,
      updateUserContact,
      getUserProfile,
      updateUserFirstAndLastName,
      setUserProfileData,
      setUserProfile,
      createAffidavit,
      firstName,
      lastName,
      emailAddress,
      confirmedEmailAddress,
      phoneNumber,
      extension,
      formError,
      editing,
      deactivateProfileDialog,
      isDeactivating,
      currentOrganization,
      userProfileData,
      syncMembership,
      syncOrganization,
      ACCOUNT_TYPE,
      isTester,
      isReseting,
      currentUser,
      $refs,
      emailRules,
      phoneRules,
      extensionRules,
      firstNameRules,
      lastNameRules,
      isInEditNameMode,
      isBCEIDUser,
      enablePaymentMethodSelectorStep,
      emailMustMatch,
      isFormValid,
      save,
      next,
      createAccount,
      saveOrUpdateContact,
      redirectToNext,
      cancel,
      navigateBack,
      goBack,
      deactivate,
      cancelConfirmDeactivate,
      reset,
      cancelConfirmReset,
    };
  },
});
