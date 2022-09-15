import {
  defineComponent,
  toRefs,
  ref,
  computed,
  watch,
  PropType,
} from "@vue/composition-api";
import { AccessType, Account, PaymentTypes } from "@/util/constants";
import { Component, Emit, Prop, Vue, Watch } from "vue-property-decorator";
import { Organization } from "@/models/Organization";
export default defineComponent({
  props: {
    organization: {
      default: undefined,
      type: Object as PropType<Organization>,
    },
    viewOnlyMode: { default: true, type: Boolean },
    canChangeAccessType: { default: false, type: Boolean },
    currentOrgPaymentType: { default: undefined, type: String },
  },
  setup(props, ctx) {
    const {
      organization,
      viewOnlyMode,
      canChangeAccessType,
      currentOrgPaymentType,
    } = toRefs(props);
    const $refs = ref<{
      accountAccessTypeForm: HTMLFormElement;
      selectedAccessType: HTMLFormElement;
    }>(undefined);
    const selectedAccessType = ref<string>(undefined);
    const AccessType = ref(AccessType);
    const isLoading = ref(false);
    const isPad = computed((): boolean => {
      return (
        currentOrgPaymentType.value &&
        currentOrgPaymentType.value === PaymentTypes.PAD
      );
    });
    const isChangeButtonEnabled = computed((): boolean => {
      const accessType: any = organization.value.accessType;
      const isAllowedAccessType =
        organization.value.orgType === Account.PREMIUM &&
        [
          AccessType.REGULAR,
          AccessType.EXTRA_PROVINCIAL,
          AccessType.REGULAR_BCEID,
        ].includes(accessType);
      return isAllowedAccessType && canChangeAccessType.value;
    });
    const getAccessTypeText = computed((): string => {
      let accessTypeText = "Regular Access";
      if (organization.value.accessType === AccessType.GOVN) {
        accessTypeText = "Government agency (other than BC provincial)";
      } else if (organization.value.accessType === AccessType.GOVM) {
        accessTypeText = "BC Government Ministry";
      }
      return accessTypeText;
    });
    const onOrganizationChange = () => {
      selectedAccessType.value =
        organization.value.accessType === AccessType.GOVN
          ? AccessType.GOVN
          : AccessType.REGULAR;
    };
    const selectedAccessTypeRules = (): any => {
      return selectedAccessType.value === AccessType.GOVN
        ? true
        : "Please select Government agency";
    };
    const updateDetails = () => {
      if (isPad.value && ctx.refs.accountAccessTypeForm.validate()) {
        ctx.emit(
          "update:updateAndSaveAccessTypeDetails",
          selectedAccessType.value
        );
      }
    };
    const cancelEdit = () => {
      selectedAccessType.value =
        organization.value.accessType === AccessType.GOVN
          ? AccessType.GOVN
          : AccessType.REGULAR;
      return {
        component: "accessType",
        mode: true,
      };
    };
    watch(organization, onOrganizationChange, { deep: true, immediate: true });
    return {
      $refs,
      selectedAccessType,
      AccessType,
      isLoading,
      isPad,
      isChangeButtonEnabled,
      getAccessTypeText,
      onOrganizationChange,
      selectedAccessTypeRules,
      updateDetails,
      cancelEdit,
    };
  },
});
