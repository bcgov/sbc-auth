import {
  defineComponent,
  computed,
  ref,
  onMounted,
} from "@vue/composition-api";
import { Business, FolioNumberload } from "@/models/business";
import { Component, Vue } from "vue-property-decorator";
import { mapActions, mapState } from "vuex";
import BusinessModule from "@/store/modules/business";
import ConfigHelper from "@/util/config-helper";
import { Contact } from "@/models/contact";
import { Organization } from "@/models/Organization";
import { SessionStorageKeys } from "@/util/constants";
import { getModule } from "vuex-module-decorators";
import { mask } from "vue-the-mask";
export default defineComponent({
  directives: {
    mask,
  },
  props: {},
  setup(_props, ctx) {
    const currentBusiness = computed(
      () => ctx.root.$store.state.business.currentBusiness
    );
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const saveContact = () => ctx.root.$store.dispatch("business/saveContact");
    const updateFolioNumber = () =>
      ctx.root.$store.dispatch("business/updateFolioNumber");
    const emailAddress = ref("");
    const confirmedEmailAddress = ref("");
    const phoneNumber = ref("");
    const extension = ref("");
    const folioNumber = ref("");
    const formError = ref("");
    const editing = ref(false);
    const currentBusiness = ref<Business>(undefined);
    const saveContact = ref<(contact: Contact) => void>(undefined);
    const updateFolioNumber =
      ref<(folioNumberload: FolioNumberload) => void>(undefined);
    const currentOrganization = ref<Organization>(undefined);
    const emailRules = ref([
      (v) => !!v || "Email address is required",
      (v) => {
        const pattern =
          /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return pattern.test(v) || "Valid email is required";
      },
    ]);
    const extensionRules = ref([
      (v) => !v || (v.length >= 0 && v.length <= 5) || "Extension is invalid",
    ]);
    const emailMustMatch = (): string => {
      return emailAddress.value === confirmedEmailAddress.value
        ? ""
        : "Email addresses must match";
    };
    const isFormValid = (): boolean => {
      if (!ctx.refs || !ctx.refs.form) {
        return false;
      }
      return (
        (
          ctx.refs.form as Vue & {
            validate: () => boolean;
          }
        ).validate() && emailAddress.value === confirmedEmailAddress.value
      );
    };
    const redirectToNext = () => {
      if (ctx.root.$route.query.redirect) {
        ctx.root.$router.push({
          path: `/account/${currentOrganization.value.id}`,
        });
      } else {
        window.location.href = `${ConfigHelper.getBusinessURL()}${
          currentBusiness.value.businessIdentifier
        }`;
      }
    };
    const save = async () => {
      if (isFormValid()) {
        const contact: Contact = {
          email: emailAddress.value.toLowerCase(),
          phone: phoneNumber.value,
          phoneExtension: extension.value,
        };
        await saveContact.value(contact);
        await updateFolioNumber.value({
          businessIdentifier: currentBusiness.value.businessIdentifier
            .trim()
            .toUpperCase(),
          folioNumber: folioNumber.value,
        });
        redirectToNext();
      }
    };
    const cancel = () => {
      redirectToNext();
    };
    onMounted(async () => {
      if (
        currentBusiness.value.contacts &&
        currentBusiness.value.contacts.length > 0
      ) {
        const contact = currentBusiness.value.contacts[0];
        emailAddress.value = confirmedEmailAddress.value = contact.email;
        phoneNumber.value = contact.phone;
        extension.value = contact.phoneExtension;
      }
      folioNumber.value = currentBusiness.value.folioNumber;
    });
    return {
      currentBusiness,
      currentOrganization,
      saveContact,
      updateFolioNumber,
      emailAddress,
      confirmedEmailAddress,
      phoneNumber,
      extension,
      folioNumber,
      formError,
      editing,
      currentBusiness,
      saveContact,
      updateFolioNumber,
      currentOrganization,
      emailRules,
      extensionRules,
      emailMustMatch,
      isFormValid,
      redirectToNext,
      save,
      cancel,
    };
  },
});
