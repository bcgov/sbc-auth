import {
  defineComponent,
  computed,
  ref,
  onMounted,
} from "@vue/composition-api";
import { Component, Mixins, Prop } from "vue-property-decorator";
import {
  CreateRequestBody,
  OrgPaymentDetails,
  Organization,
  PADInfo,
  PADInfoValidation,
} from "@/models/Organization";
import { mapActions, mapMutations, mapState } from "vuex";
import PADInfoForm from "@/components/auth/common/PADInfoForm.vue";
import { PaymentTypes } from "@/util/constants";
import Steppable from "@/components/auth/common/stepper/Steppable.vue";
export default defineComponent({
  components: {
    PADInfoForm,
  },
  props: {},
  setup(_props, ctx) {
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const getOrgPayments = () => ctx.root.$store.dispatch("org/getOrgPayments");
    const updateOrg = () => ctx.root.$store.dispatch("org/updateOrg");
    const validatePADInfo = () =>
      ctx.root.$store.dispatch("org/validatePADInfo");
    const currentOrganization = ref<Organization>(undefined);
    const updateOrg =
      ref<(requestBody: CreateRequestBody) => Promise<Organization>>(undefined);
    const validatePADInfo = ref<() => Promise<PADInfoValidation>>(undefined);
    const getOrgPayments = ref<() => any>(undefined);
    const padInfo = ref<PADInfo>({} as PADInfo);
    const padValid = ref<boolean>(false);
    const refreshPAD = ref(0);
    const orgPadInfo = ref<PADInfo>({} as PADInfo);
    const isLoading = ref<boolean>(false);
    const errorText = ref<string>("");
    const isTouched = ref<boolean>(false);
    const goNext = async () => {
      if (!isTouched.value) {
        stepForward();
      } else {
        isLoading.value = true;
        let isValid = isTouched.value ? await verifyPAD() : true;
        if (isValid) {
          const createRequestBody: CreateRequestBody = {
            paymentInfo: {
              paymentMethod: PaymentTypes.PAD,
              bankTransitNumber: padInfo.value.bankTransitNumber,
              bankInstitutionNumber: padInfo.value.bankInstitutionNumber,
              bankAccountNumber: padInfo.value.bankAccountNumber,
            },
          };
          try {
            await updateOrg.value(createRequestBody);
            isLoading.value = false;
            stepForward();
          } catch (error) {
            console.error(error);
            isLoading.value = false;
          }
        }
      }
    };
    const goBack = () => {
      stepBack();
    };
    const getPADInfo = (padInfo: PADInfo) => {
      padInfo.value = padInfo;
    };
    const isPADValid = (isValid) => {
      padValid.value = isValid;
    };
    const isPadInfoTouched = (isTouched) => {
      isTouched.value = isTouched;
    };
    const verifyPAD = async () => {
      errorText.value = "";
      const verifyPad: PADInfoValidation = await validatePADInfo.value();
      if (!verifyPad) {
        return true;
      }
      if (verifyPad?.isValid) {
        return true;
      }
      isLoading.value = false;
      errorText.value = "Bank information validation failed";
      if (verifyPad?.message?.length) {
        let msgList = "";
        verifyPad.message.forEach((msg) => {
          msgList += `<li>${msg}</li>`;
        });
        errorText.value = `<ul class="error-list">${msgList}</ul>`;
      }
      return false;
    };
    onMounted(async () => {
      const orgPayments: OrgPaymentDetails = await getOrgPayments.value();
      const cfsAccount = orgPayments?.cfsAccount;
      padInfo.value.bankAccountNumber = cfsAccount?.bankAccountNumber;
      padInfo.value.bankInstitutionNumber = cfsAccount?.bankInstitutionNumber;
      padInfo.value.bankTransitNumber = cfsAccount?.bankTransitNumber;
      padInfo.value.isTOSAccepted = !!(
        cfsAccount?.bankAccountNumber &&
        cfsAccount?.bankInstitutionNumber &&
        cfsAccount?.bankTransitNumber
      );
      refreshPAD.value++;
    });
    return {
      currentOrganization,
      getOrgPayments,
      updateOrg,
      validatePADInfo,
      currentOrganization,
      updateOrg,
      validatePADInfo,
      getOrgPayments,
      padInfo,
      padValid,
      refreshPAD,
      orgPadInfo,
      isLoading,
      errorText,
      isTouched,
      goNext,
      goBack,
      getPADInfo,
      isPADValid,
      isPadInfoTouched,
      verifyPAD,
    };
  },
});
