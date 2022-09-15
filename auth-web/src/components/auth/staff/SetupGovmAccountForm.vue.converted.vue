import { defineComponent, ref } from "@vue/composition-api";
import { AccessType, Account, Pages } from "@/util/constants";
import { Component, Vue } from "vue-property-decorator";
import {
  CreateRequestBody,
  MembershipType,
  Organization,
} from "@/models/Organization";
import CommonUtils from "@/util/common-util";
import ModalDialog from "@/components/auth/common/ModalDialog.vue";
import { namespace } from "vuex-class";
const OrgModule = namespace("org");
export default defineComponent({
  components: {
    ModalDialog,
  },
  props: {},
  setup(_props, ctx) {
    const ministryName = ref<string>("");
    const branchName = ref<string>("");
    const errorMessage = ref<string>("");
    const saving = ref(false);
    const loader = ref(false);
    const email = ref("");
    const emailConfirm = ref("");
    const dialogTitle = ref("");
    const dialogText = ref("");
    const emailRules = ref(CommonUtils.emailRules());
    const $refs = ref<{
      setupGovmAccountForm: HTMLFormElement;
      errorDialog: ModalDialog;
    }>(undefined);
    const ministryNameRules = ref([
      (v) => !!v || "A ministry name is required",
    ]);
    const emailMatchError = () => {
      return email.value === emailConfirm.value
        ? null
        : "Email Address does not match";
    };
    const isFormValid = (): boolean => {
      return (
        !!ministryName.value &&
        !emailMatchError() &&
        ctx.refs.setupGovmAccountForm.validate()
      );
    };
    const save = async () => {
      loader.value = saving.value;
      if (isFormValid()) {
        const createRequestBody: CreateRequestBody = {
          name: ministryName.value,
          accessType: AccessType.GOVM,
          branchName: branchName.value,
          typeCode: Account.PREMIUM,
        };
        try {
          saving.value = true;
          const organization = await createOrgByStaff(createRequestBody);
          await createInvitation({
            recipientEmail: email.value,
            sentDate: new Date(),
            membership: [
              { membershipType: MembershipType.Admin, orgId: organization.id },
            ],
          });
          saving.value = false;
          loader.value = saving.value;
          ctx.root.$router.push({
            path: `/staff-setup-account-success/${AccessType.GOVM.toLowerCase()}/${
              ministryName.value
            }`,
          });
        } catch (err) {
          saving.value = false;
          switch (err.response.status) {
            case 409:
              errorMessage.value =
                "An account with this name already exists. Try a different account name.";
              break;
            case 400:
              if (err.response.data.code === "MAX_NUMBER_OF_ORGS_LIMIT") {
                errorMessage.value = "Maximum number of accounts reached";
              } else {
                errorMessage.value = "Invalid account name";
              }
              break;
            default:
              errorMessage.value =
                "Something went wrong while attempting to create this account. Please try again later.";
          }
          showEntityNotFoundModal(errorMessage.value);
          loader.value = saving.value;
        }
      }
    };
    const cancel = () => {
      ctx.root.$router.push({ path: Pages.STAFF_DASHBOARD });
    };
    const showEntityNotFoundModal = (msg?) => {
      dialogTitle.value = "An error has occured";
      dialogText.value =
        msg ||
        "Something went wrong while attempting to create this account. Please try again later.";
      ctx.refs.errorDialog.open();
    };
    const close = () => {
      ctx.refs.errorDialog.close();
    };
    return {
      ministryName,
      branchName,
      errorMessage,
      saving,
      loader,
      email,
      emailConfirm,
      dialogTitle,
      dialogText,
      emailRules,
      $refs,
      ministryNameRules,
      emailMatchError,
      isFormValid,
      save,
      cancel,
      showEntityNotFoundModal,
      close,
    };
  },
});
