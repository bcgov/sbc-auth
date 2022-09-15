import { defineComponent, toRefs, ref } from "@vue/composition-api";
import { Component, Emit, Prop } from "vue-property-decorator";
import ModalDialog from "@/components/auth/common/ModalDialog.vue";
import Vue from "vue";
import { mapActions } from "vuex";
import { namespace } from "vuex-class";
const OrgModule = namespace("org");
export default defineComponent({
  components: {
    ModalDialog,
  },
  props: {
    isEmit: { default: false, type: Boolean },
    showConfirmPopup: { default: true, type: Boolean },
    disabled: { default: false, type: Boolean },
    mainText: { default: "Cancel Account Creation", type: String },
    subText: {
      default: "Are you sure you want to cancel your account creation set-up?",
      type: String,
    },
    confirmBtnText: { default: "Yes", type: String },
    rejectBtnText: { default: "No", type: String },
    targetRoute: { default: "/", type: String },
    clearCurrentOrg: { default: true, type: Boolean },
  },
  setup(props, ctx) {
    const {
      isEmit,
      showConfirmPopup,
      disabled,
      mainText,
      subText,
      confirmBtnText,
      rejectBtnText,
      targetRoute,
      clearCurrentOrg,
    } = toRefs(props);
    const $refs = ref<{
      confirmCancelDialog: ModalDialog;
    }>(undefined);
    const confirmDialogResponse = async (response) => {
      if (response) {
        clickConfirm();
      }
      ctx.refs.confirmCancelDialog.close();
    };
    const clickConfirm = async () => {
      try {
        if (clearCurrentOrg.value) {
          await resetAccountSetupProgress();
          await setCurrentOrganizationFromUserAccountSettings();
          await ctx.root.$store.commit("updateHeader");
        }
        if (isEmit.value) {
          emitClickConfirm();
        } else {
          ctx.root.$router.push(targetRoute.value);
        }
      } catch (err) {
        console.log("Error while cancelling account creation flow", err);
      }
    };
    const emitClickConfirm = () => {};
    const openModalDialog = () => {
      if (showConfirmPopup.value) {
        ctx.refs.confirmCancelDialog.open();
      } else {
        clickConfirm();
      }
    };
    return {
      $refs,
      confirmDialogResponse,
      clickConfirm,
      emitClickConfirm,
      openModalDialog,
    };
  },
});
