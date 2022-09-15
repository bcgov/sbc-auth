import { defineComponent, toRefs, computed } from "@vue/composition-api";
import { Component, Prop } from "vue-property-decorator";
import Vue from "vue";
import { paymentErrorType } from "@/util/constants";
export default defineComponent({
  props: {
    errorType: { default: "GENERIC_ERROR", type: String },
    backUrl: { default: "", type: String },
    tryAgainURL: { default: "", type: String },
  },
  setup(props, ctx) {
    const { errorType, backUrl, tryAgainURL } = toRefs(props);
    const error = computed(() => {
      let errorTitle = "";
      let errorMessage = "";
      let errorIcon = "mdi-alert-circle-outline";
      let showOkbtn = false;
      let showCancelbtn = true;
      switch (errorType.value) {
        case paymentErrorType.GENERIC_ERROR:
          errorTitle = ctx.root.$t("paymentErrorTitle").toString();
          errorMessage = ctx.root.$t("paymentErrorSubText").toString();
          break;
        case paymentErrorType.PAYMENT_CANCELLED:
          errorTitle = ctx.root.$t("paymentCancelTitle").toString();
          errorMessage = ctx.root.$t("paymentCancelSubText").toString();
          break;
        case paymentErrorType.DECLINED:
          errorTitle = ctx.root.$t("paymentDeclinedTitle").toString();
          errorMessage = ctx.root.$t("paymentDeclinedSubText").toString();
          break;
        case paymentErrorType.INVALID_CARD_NUMBER:
          errorTitle = ctx.root.$t("paymentInvalidErrorTitle").toString();
          errorMessage = ctx.root.$t("paymentInvalidErrorSubText").toString();
          break;
        case paymentErrorType.DECLINED_EXPIRED_CARD:
          errorTitle = ctx.root.$t("paymentExpiredCardErrorTitle").toString();
          errorMessage = ctx.root
            .$t("paymentExpiredCardErrorSubText")
            .toString();
          break;
        case paymentErrorType.DUPLICATE_ORDER_NUMBER:
          errorTitle = ctx.root.$t("paymentDuplicateErrorTitle").toString();
          errorMessage = ctx.root.$t("paymentDuplicateErrorSubText").toString();
          showOkbtn = true;
          showCancelbtn = false;
          break;
        case paymentErrorType.TRANSACTION_TIMEOUT_NO_DEVICE:
          errorTitle = ctx.root.$t("paymentTimeoutErrorTitle").toString();
          errorMessage = ctx.root.$t("paymentTimeoutErrorSubText").toString();
          errorIcon = "mdi-clock-outline";
          break;
        case paymentErrorType.VALIDATION_ERROR:
          errorTitle = ctx.root.$t("paymentValidationErrorTitle").toString();
          errorMessage = ctx.root
            .$t("paymentValidationErrorSubText")
            .toString();
          break;
        default:
          errorTitle = ctx.root.$t("paymentErrorTitle").toString();
          errorMessage = ctx.root.$t("paymentErrorSubText").toString();
          break;
      }
      return { errorTitle, errorMessage, errorIcon, showOkbtn, showCancelbtn };
    });
    const tryAgain = () => {
      ctx.root.$router.push(tryAgainURL.value);
    };
    return { error, tryAgain };
  },
});
