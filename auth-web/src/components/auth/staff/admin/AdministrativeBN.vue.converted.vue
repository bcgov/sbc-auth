import { defineComponent, ref, onMounted } from "@vue/composition-api";
import { BNRequest } from "@/models/request-tracker";
import BNRequestManager from "@/components/auth/staff/admin/BNRequestManager.vue";
import CommonUtils from "@/util/common-util";
import { Component } from "vue-property-decorator";
import ConfigHelper from "@/util/config-helper";
import { LearBusiness } from "@/models/business";
import { SessionStorageKeys } from "@/util/constants";
import Vue from "vue";
import { mask } from "vue-the-mask";
import { namespace } from "vuex-class";
const BusinessModule = namespace("business");
export default defineComponent({
  components: {
    BNRequestManager,
  },
  directives: { mask },
  props: {},
  setup(_props, ctx) {
    const $refs = ref<{
      searchBusinessForm: HTMLFormElement;
      submitBNRequestForm: HTMLFormElement;
    }>(undefined);
    const businessIdentifier = ref("");
    const searchedBusinessIdentifier = ref("");
    const searchActive = ref(false);
    const errorMessage = ref("");
    const businessDetails = ref<LearBusiness>(null);
    const requestCRA = ref(false);
    const businessNumber = ref("");
    const submitActive = ref(false);
    const submitBNRequestErrorMessage = ref("");
    const requestQueued = ref(false);
    const businessIdentifierRules = ref([
      (v) => !!v || "Incorporation Number or Registration Number is required",
      (v) =>
        CommonUtils.validateIncorporationNumber(v) ||
        "Incorporation Number or Registration Number is not valid",
    ]);
    const businessNumberRules = ref([
      (v: string) => {
        const pattern = /^[0-9]{9}$/;
        return !v || pattern.test(v) || "Invalid business number";
      },
    ]);
    const isFormValid = (): boolean => {
      return (
        !!businessIdentifier.value && ctx.refs.searchBusinessForm?.validate()
      );
    };
    const search = async () => {
      searchActive.value = true;
      try {
        errorMessage.value = "";
        businessDetails.value = await searchBusiness(businessIdentifier.value);
      } catch (exception) {
        businessDetails.value = null;
        searchedBusinessIdentifier.value = businessIdentifier.value;
        errorMessage.value = ctx.root
          .$t("noIncorporationNumberFound")
          .toString();
      } finally {
        searchActive.value = false;
      }
    };
    const resetSearch = () => {
      businessDetails.value = null;
      searchedBusinessIdentifier.value = null;
      businessIdentifier.value = null;
      ConfigHelper.removeFromSession(SessionStorageKeys.BusinessIdentifierKey);
    };
    const reload = () => {
      window.location.reload();
    };
    const formatBusinessIdentifier = () => {
      businessIdentifier.value = CommonUtils.formatIncorporationNumber(
        businessIdentifier.value
      );
    };
    const canRequestNewBN = (): boolean => {
      return (
        businessDetails.value &&
        (!businessDetails.value.taxId ||
          businessDetails.value.taxId.length < 15)
      );
    };
    const isBNRequestFormValid = (): boolean => {
      return requestCRA.value && ctx.refs.submitBNRequestForm?.validate();
    };
    const submitBNRequest = async () => {
      if (isBNRequestFormValid()) {
        submitActive.value = true;
        requestQueued.value = false;
        try {
          submitBNRequestErrorMessage.value = "";
          await createBNRequest({
            businessIdentifier: businessIdentifier.value,
            businessNumber: businessNumber.value,
          });
          ctx.refs.submitBNRequestForm?.reset();
          requestQueued.value = true;
        } catch (exception) {
          submitBNRequestErrorMessage.value = exception;
        } finally {
          submitActive.value = false;
        }
      }
    };
    onMounted(async () => {
      const identifier = ConfigHelper.getFromSession(
        SessionStorageKeys.BusinessIdentifierKey
      );
      if (identifier) {
        businessIdentifier.value = identifier;
        await search();
      }
    });
    return {
      $refs,
      businessIdentifier,
      searchedBusinessIdentifier,
      searchActive,
      errorMessage,
      businessDetails,
      requestCRA,
      businessNumber,
      submitActive,
      submitBNRequestErrorMessage,
      requestQueued,
      businessIdentifierRules,
      businessNumberRules,
      isFormValid,
      search,
      resetSearch,
      reload,
      formatBusinessIdentifier,
      canRequestNewBN,
      isBNRequestFormValid,
      submitBNRequest,
    };
  },
});
