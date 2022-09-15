import { defineComponent, computed, ref } from "@vue/composition-api";
import { Component, Vue } from "vue-property-decorator";
import { mapActions, mapState } from "vuex";
import CommonUtils from "@/util/common-util";
import { CreateNRAffiliationRequestBody } from "@/models/affiliation";
import HelpDialog from "@/components/auth/common/HelpDialog.vue";
import { Organization } from "@/models/Organization";
import { StatusCodes } from "http-status-codes";
export default defineComponent({
  components: {
    HelpDialog,
  },
  props: {},
  setup(_props, ctx) {
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const addNameRequest = () =>
      ctx.root.$store.dispatch("business/addNameRequest");
    const currentOrganization = ref<Organization>(undefined);
    const addNameRequest =
      ref<(requestBody: CreateNRAffiliationRequestBody) => any>(undefined);
    const helpDialogBlurb = ref(
      "If you have lost your receipt and name results email and " +
        "need assistance finding your Name Request (NR) Number, please contact use at:"
    );
    const nrNumberRules = ref([
      (v) => !!v || "Name Request Number is required",
      (v) =>
        CommonUtils.validateNameRequestNumber(v) ||
        "Name Request Number is invalid",
    ]);
    const applicantPhoneNumberRules = ref([
      (v) => isInputEntered(v, "phone") || "Phone number is required",
      (v) => CommonUtils.validatePhoneNumber(v) || "Phone number is invalid",
    ]);
    const applicantEmailRules = ref([
      (v) => isInputEntered(v, "email") || "Email is required",
      (v) => isValidateEmail(v) || "Email is Invalid",
    ]);
    const nrNumber = ref("");
    const applicantPhoneNumber = ref("");
    const applicantEmail = ref("");
    const isLoading = ref(false);
    const $refs = ref<{
      addNRForm: HTMLFormElement;
      helpDialog: HelpDialog;
    }>(undefined);
    const isFormValid = (): boolean => {
      return (
        !!nrNumber.value &&
        (!!applicantPhoneNumber.value || !!applicantEmail.value)
      );
    };
    const isInputEntered = (value: any, inputType: string): boolean => {
      return (
        !!(inputType === "email"
          ? applicantPhoneNumber.value
          : applicantEmail.value) || !!value
      );
    };
    const isValidateEmail = (value: any): boolean => {
      return (
        (!!applicantPhoneNumber.value && !!value) ||
        !!CommonUtils.validateEmailFormat(value)
      );
    };
    const add = async (): Promise<void> => {
      if (isFormValid()) {
        isLoading.value = true;
        try {
          const nrResponse = await addNameRequest.value({
            businessIdentifier: nrNumber.value,
            phone: applicantPhoneNumber.value.replace(/-/g, ""),
            email: applicantEmail.value,
          });
          if (nrResponse?.status === 201) {
            ctx.emit("add-success");
          } else {
            ctx.emit("add-unknown-error");
          }
        } catch (exception) {
          if (exception.response?.status === StatusCodes.BAD_REQUEST) {
            ctx.emit(
              "add-failed-show-msg",
              exception.response?.data?.message || ""
            );
          } else if (exception.response?.status === StatusCodes.NOT_FOUND) {
            ctx.emit("add-failed-no-entity");
          } else {
            ctx.emit("add-unknown-error");
          }
        } finally {
          resetForm("");
        }
      }
    };
    const resetForm = (event: string): void => {
      nrNumber.value = "";
      applicantEmail.value = "";
      applicantPhoneNumber.value = "";
      ctx.refs.addNRForm.resetValidation();
      isLoading.value = false;
      if (event) {
        ctx.emit("on-cancel");
      }
    };
    const formatNrNumber = (): void => {
      nrNumber.value = CommonUtils.formatIncorporationNumber(
        nrNumber.value,
        true
      );
    };
    const openHelp = (): void => {
      ctx.refs.helpDialog.open();
    };
    return {
      currentOrganization,
      addNameRequest,
      currentOrganization,
      addNameRequest,
      helpDialogBlurb,
      nrNumberRules,
      applicantPhoneNumberRules,
      applicantEmailRules,
      nrNumber,
      applicantPhoneNumber,
      applicantEmail,
      isLoading,
      $refs,
      isFormValid,
      isInputEntered,
      isValidateEmail,
      add,
      resetForm,
      formatNrNumber,
      openHelp,
    };
  },
});
