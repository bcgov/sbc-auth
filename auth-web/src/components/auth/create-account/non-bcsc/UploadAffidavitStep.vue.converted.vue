import {
  defineComponent,
  computed,
  toRefs,
  ref,
  onMounted,
} from "@vue/composition-api";
import { Component, Mixins, Prop } from "vue-property-decorator";
import { NotaryContact, NotaryInformation } from "@/models/notary";
import { mapActions, mapMutations, mapState } from "vuex";
import { Account } from "@/util/constants";
import { Address } from "@/models/address";
import ConfirmCancelButton from "@/components/auth/common/ConfirmCancelButton.vue";
import FileUploadPreview from "@/components/auth/common/FileUploadPreview.vue";
import NotaryContactForm from "@/components/auth/create-account/non-bcsc/NotaryContactForm.vue";
import NotaryInformationForm from "@/components/auth/create-account/non-bcsc/NotaryInformationForm.vue";
import OrgModule from "@/store/modules/org";
import { Organization } from "@/models/Organization";
import Steppable from "@/components/auth/common/stepper/Steppable.vue";
import UserModule from "@/store/modules/user";
import { getModule } from "vuex-module-decorators";
export default defineComponent({
  components: {
    NotaryInformationForm,
    NotaryContactForm,
    ConfirmCancelButton,
    FileUploadPreview,
  },
  props: {
    isAffidavitUpload: { default: false, type: Boolean },
    cancelUrl: { type: String },
  },
  setup(props, ctx) {
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const userProfile = computed(() => ctx.root.$store.state.user.userProfile);
    const currentUser = computed(() => ctx.root.$store.state.user.currentUser);
    const notaryInformation = computed(
      () => ctx.root.$store.state.user.notaryInformation
    );
    const notaryContact = computed(
      () => ctx.root.$store.state.user.notaryContact
    );
    const affidavitDoc = computed(
      () => ctx.root.$store.state.user.affidavitDoc
    );
    const uploadPendingDocsToStorage = () =>
      ctx.root.$store.dispatch("user/uploadPendingDocsToStorage");
    const { isAffidavitUpload, cancelUrl } = toRefs(props);
    const orgStore = ref(getModule(OrgModule, ctx.root.$store));
    const userStore = ref(getModule(UserModule, ctx.root.$store));
    const errorMessage = ref<string>("");
    const saving = ref<boolean>(false);
    const MAX_FILE_SIZE = ref(10000);
    const isNotaryContactValid = ref<boolean>(false);
    const isNotaryInformationValid = ref<boolean>(false);
    const isFileUploadValid = ref<boolean>(false);
    const notaryInformation = ref<NotaryInformation>(undefined);
    const affidavitDoc = ref<File>(undefined);
    const notaryContact = ref<NotaryContact>(undefined);
    const uploadPendingDocsToStorage = ref<() => void>(undefined);
    const setNotaryInformation =
      ref<(notaryInformation: NotaryInformation) => void>(undefined);
    const setAffidavitDoc = ref<(affidavitDoc: File) => void>(undefined);
    const setNotaryContact =
      ref<(notaryContact: NotaryContact) => void>(undefined);
    const currentOrganization = ref<Organization>(undefined);
    const isNextValid = computed(() => {
      return (
        isFileUploadValid.value &&
        isNotaryInformationValid.value &&
        isNotaryContactValid.value
      );
    });
    const next = async () => {
      try {
        errorMessage.value = "";
        saving.value = true;
        await uploadPendingDocsToStorage.value();
        if (isAffidavitUpload.value) {
          ctx.emit("emit-admin-affidavit-complete");
        } else {
          stepForward(currentOrganization.value?.orgType === Account.PREMIUM);
        }
      } catch (error) {
        errorMessage.value = `Something happend while uploading the document, please try again`;
        console.error(error);
      } finally {
        saving.value = false;
      }
    };
    const redirectToNext = (organization?: Organization) => {
      ctx.root.$router.push({ path: `/account/${organization.id}/` });
    };
    const goBack = () => {
      stepBack();
    };
    const goNext = async () => {
      stepForward();
    };
    const fileSelected = (file) => {
      errorMessage.value = "";
      setAffidavitDoc.value(file);
    };
    const updateNotaryInformation = (notaryInfo: NotaryInformation) => {
      setNotaryInformation.value(notaryInfo);
    };
    const updateNotaryContact = (notaryContact: NotaryContact) => {
      setNotaryContact.value(notaryContact);
    };
    const isNotaryContactValidFn = (val) => {
      isNotaryContactValid.value = val;
    };
    const isNotaryInformationValidFn = (val) => {
      isNotaryInformationValid.value = val;
    };
    const isFileUploadValidFn = (val) => {
      isFileUploadValid.value = val;
    };
    onMounted(async () => {
      errorMessage.value = "";
      if (!notaryInformation.value) {
        setNotaryInformation.value({ notaryName: "", address: {} as Address });
      }
    });
    return {
      currentOrganization,
      userProfile,
      currentUser,
      notaryInformation,
      notaryContact,
      affidavitDoc,
      uploadPendingDocsToStorage,
      orgStore,
      userStore,
      errorMessage,
      saving,
      MAX_FILE_SIZE,
      isNotaryContactValid,
      isNotaryInformationValid,
      isFileUploadValid,
      notaryInformation,
      affidavitDoc,
      notaryContact,
      uploadPendingDocsToStorage,
      setNotaryInformation,
      setAffidavitDoc,
      setNotaryContact,
      currentOrganization,
      isNextValid,
      next,
      redirectToNext,
      goBack,
      goNext,
      fileSelected,
      updateNotaryInformation,
      updateNotaryContact,
      isNotaryContactValidFn,
      isNotaryInformationValidFn,
      isFileUploadValidFn,
    };
  },
});
