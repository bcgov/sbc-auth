import {
  defineComponent,
  toRefs,
  ref,
  computed,
  watch,
} from "@vue/composition-api";
import { Component, Prop, Vue, Watch } from "vue-property-decorator";
import { FolioNumberload, LoginPayload } from "@/models/business";
import Certify from "./Certify.vue";
import CommonUtils from "@/util/common-util";
import HelpDialog from "@/components/auth/common/HelpDialog.vue";
import { StatusCodes } from "http-status-codes";
import { mapActions } from "vuex";
export default defineComponent({
  components: {
    Certify,
    HelpDialog,
  },
  props: { dialog: { default: false, type: Boolean } },
  setup(props, ctx) {
    const addBusiness = () => ctx.root.$store.dispatch("business/addBusiness");
    const updateBusinessName = () =>
      ctx.root.$store.dispatch("business/updateBusinessName");
    const updateFolioNumber = () =>
      ctx.root.$store.dispatch("business/updateFolioNumber");
    const { dialog } = toRefs(props);
    const $refs = ref<{
      addBusinessForm: HTMLFormElement;
      helpDialog: HelpDialog;
    }>(undefined);
    const addBusiness = ref<(loginPayload: LoginPayload) => any>(undefined);
    const updateBusinessName = ref<(businessNumber: string) => any>(undefined);
    const updateFolioNumber =
      ref<(folioNumberload: FolioNumberload) => void>(undefined);
    const businessIdentifier = ref("");
    const passcode = ref("");
    const folioNumber = ref("");
    const isLoading = ref(false);
    const isCertified = ref(false);
    const businessIdentifierRules = ref([
      (v) => !!v || "Incorporation Number or Registration Number is required",
      (v) =>
        CommonUtils.validateIncorporationNumber(v) ||
        "Incorporation Number or Registration Number is not valid",
    ]);
    const certifyClause = ref(
      "Note: It is an offence to make or assist in making a false or misleading " +
        "statement in a record filed under the Partnership Act. A person who commits this offence is " +
        "subject to a maximum fine of $5,000."
    );
    const isBusinessIdentifierValid = computed((): boolean => {
      return CommonUtils.validateIncorporationNumber(businessIdentifier.value);
    });
    const isCooperative = computed((): boolean => {
      return CommonUtils.isCooperativeNumber(businessIdentifier.value);
    });
    const isFirm = computed((): boolean => {
      return CommonUtils.isFirmNumber(businessIdentifier.value);
    });
    const passcodeLabel = computed((): string => {
      if (isFirm.value) return "Proprietor or Partner Name";
      if (isCooperative.value) return "Passcode";
      return "Password";
    });
    const passcodeHint = computed((): string => {
      if (isFirm.value)
        return "Name as it appears on the Business Summary or the Statement of Registration";
      if (isCooperative.value) return "Passcode must be exactly 9 digits";
      return "Password must be 8 to 15 characters";
    });
    const passcodeMaxLength = computed((): number => {
      if (isFirm.value) return 150;
      if (isCooperative.value) return 9;
      return 15;
    });
    const passcodeRules = computed((): any[] => {
      if (isFirm.value) {
        return [
          (v) => !!v || "Proprietor or Partner Name is required",
          (v) => v.length <= 150 || "Maximum 150 characters",
        ];
      }
      if (isCooperative.value) {
        return [
          (v) => !!v || "Passcode is required",
          (v) =>
            CommonUtils.validateCooperativePasscode(v) ||
            "Passcode must be exactly 9 digits",
        ];
      }
      return [
        (v) => !!v || "Password is required",
        (v) =>
          CommonUtils.validateCorporatePassword(v) ||
          "Password must be 8 to 15 characters",
      ];
    });
    const forgotButtonText = computed((): string => {
      return (
        "I lost or forgot my " + (isCooperative.value ? "passcode" : "password")
      );
    });
    const helpDialogBlurb = computed((): string => {
      if (isCooperative.value) {
        return (
          "If you have not received your Access Letter from BC Registries, or have lost your Passcode, " +
          "please contact us at:"
        );
      } else {
        const url = "www.corporateonline.gov.bc.ca";
        return (
          `If you have forgotten or lost your password, please visit <a href="https://${url}">${url}</a> ` +
          'and choose the option "Forgot Company Password", or contact us at:'
        );
      }
    });
    const isFormValid = computed((): boolean => {
      return (
        !!businessIdentifier.value &&
        !!passcode.value &&
        (!isFirm.value || isCertified.value) &&
        ctx.refs.addBusinessForm.validate()
      );
    });
    const add = async (): Promise<void> => {
      ctx.refs.addBusinessForm.validate();
      if (isFormValid.value) {
        isLoading.value = true;
        try {
          const addResponse = await addBusiness.value({
            businessIdentifier: businessIdentifier.value,
            passCode: passcode.value,
          });
          if (addResponse?.status !== StatusCodes.CREATED) {
            ctx.emit("add-unknown-error");
          }
          const businessResponse = await updateBusinessName.value(
            businessIdentifier.value
          );
          if (businessResponse?.status !== StatusCodes.OK) {
            ctx.emit("add-unknown-error");
          }
          await updateFolioNumber.value({
            businessIdentifier: businessIdentifier.value,
            folioNumber: folioNumber.value,
          });
          ctx.emit("add-success");
        } catch (exception) {
          if (exception.response?.status === StatusCodes.UNAUTHORIZED) {
            ctx.emit("add-failed-invalid-code", passcodeLabel.value);
          } else if (exception.response?.status === StatusCodes.NOT_FOUND) {
            ctx.emit("add-failed-no-entity");
          } else if (
            exception.response?.status === StatusCodes.NOT_ACCEPTABLE
          ) {
            ctx.emit("add-failed-passcode-claimed");
          } else {
            ctx.emit("add-unknown-error");
          }
        } finally {
          resetForm();
        }
      }
    };
    const resetForm = (emitCancel = false): void => {
      businessIdentifier.value = "";
      passcode.value = "";
      folioNumber.value = "";
      ctx.refs.addBusinessForm.resetValidation();
      isLoading.value = false;
      if (emitCancel) {
        ctx.emit("on-cancel");
      }
    };
    const formatBusinessIdentifier = (): void => {
      businessIdentifier.value = CommonUtils.formatIncorporationNumber(
        businessIdentifier.value
      );
    };
    const openHelp = (): void => {
      ctx.refs.helpDialog.open();
    };
    const onBusinessIdentifierChange = (): void => {
      ctx.emit("on-business-identifier", businessIdentifier.value);
    };
    watch(businessIdentifier, onBusinessIdentifierChange, { immediate: true });
    return {
      addBusiness,
      updateBusinessName,
      updateFolioNumber,
      $refs,
      addBusiness,
      updateBusinessName,
      updateFolioNumber,
      businessIdentifier,
      passcode,
      folioNumber,
      isLoading,
      isCertified,
      businessIdentifierRules,
      certifyClause,
      isBusinessIdentifierValid,
      isCooperative,
      isFirm,
      passcodeLabel,
      passcodeHint,
      passcodeMaxLength,
      passcodeRules,
      forgotButtonText,
      helpDialogBlurb,
      isFormValid,
      add,
      resetForm,
      formatBusinessIdentifier,
      openHelp,
      onBusinessIdentifierChange,
    };
  },
});
