import {
  defineComponent,
  computed,
  toRefs,
  ref,
  watch,
  onMounted,
} from "@vue/composition-api";
import { Component, Emit, Prop, Vue, Watch } from "vue-property-decorator";
import { mapActions, mapState } from "vuex";
import TermsOfUse from "@/components/auth/common/TermsOfUse.vue";
import { User } from "@/models/user";
import documentService from "@/services/document.services.ts";
import { getModule } from "vuex-module-decorators";
export default defineComponent({
  components: {
    TermsOfUse,
  },
  props: {
    tosType: { default: "termsofuse", type: String },
    tosHeading: { default: "Terms of Use Agreement", type: String },
    tosCheckBoxLabelAppend: { default: "", type: String },
    isUserTOS: { default: false, type: Boolean },
    isAlreadyAccepted: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const userHasToAcceptTOS = computed(
      () => ctx.root.$store.state.user.userHasToAcceptTOS
    );
    const {
      tosType,
      tosHeading,
      tosCheckBoxLabelAppend,
      isUserTOS,
      isAlreadyAccepted,
    } = toRefs(props);
    const userHasToAcceptTOS = ref<boolean>(undefined);
    const termsDialog = ref<boolean>(true);
    const termsAccepted = ref<boolean>(false);
    const canCheckTerms = ref<boolean>(false);
    const atBottom = ref<boolean>(false);
    const tooltipTxt = computed(() => {
      return "Please read and agree to the Terms Of Use";
    });
    const updateTermsAccepted = (val, oldVal) => {
      if (isUserTOS.value && val) {
        agreeToTerms();
      }
    };
    const updateIsAlreadyAccepted = (val, oldVal) => {
      if (oldVal !== val) {
        termsAccepted.value = canCheckTerms.value = val;
      }
    };
    const openDialog = () => {
      termsDialog.value = true;
    };
    const closeDialog = () => {
      termsDialog.value = false;
    };
    const onScroll = (e) => {
      atBottom.value =
        e.target.scrollHeight - e.target.scrollTop <=
        e.target.offsetHeight + 25;
    };
    const agreeToTerms = () => {
      termsDialog.value = false;
      termsAccepted.value = true;
      canCheckTerms.value = true;
      emitTermsAcceptanceStatus();
    };
    const emitTermsAcceptanceStatus = () => {
      return termsAccepted.value;
    };
    watch(userHasToAcceptTOS, updateTermsAccepted, { deep: true });
    watch(isAlreadyAccepted, updateIsAlreadyAccepted, { deep: true });
    onMounted(() => {
      termsDialog.value = false;
      if (isUserTOS.value && userHasToAcceptTOS.value) {
        agreeToTerms();
      }
      if (isAlreadyAccepted.value) {
        termsAccepted.value = canCheckTerms.value = true;
      }
    });
    return {
      userHasToAcceptTOS,
      userHasToAcceptTOS,
      termsDialog,
      termsAccepted,
      canCheckTerms,
      atBottom,
      tooltipTxt,
      updateTermsAccepted,
      updateIsAlreadyAccepted,
      openDialog,
      closeDialog,
      onScroll,
      agreeToTerms,
      emitTermsAcceptanceStatus,
    };
  },
});
