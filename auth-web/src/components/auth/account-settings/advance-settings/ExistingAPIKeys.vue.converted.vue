import { defineComponent, ref, onMounted } from "@vue/composition-api";
import { Component, Mixins } from "vue-property-decorator";
import AccountChangeMixin from "@/components/auth/mixins/AccountChangeMixin.vue";
import ModalDialog from "@/components/auth/common/ModalDialog.vue";
import { Organization } from "@/models/Organization";
import { namespace } from "vuex-class";
const OrgModule = namespace("org");
export default defineComponent({
  components: {
    ModalDialog,
  },
  props: {},
  setup(_props, ctx) {
    const isLoading = ref(true);
    const confirmActionTitle = ref("Revoke API Key?");
    const confirmActionTextLine1 = ref("");
    const confirmActionTextLine2 = ref("");
    const alertText = ref("");
    const alertTitle = ref("");
    const alertIcon = ref("mdi-check");
    const notificationColor = ref("success");
    const totalApiKeyCount = ref<number>(0);
    const selectedApi = ref<any>({});
    const $refs = ref<{
      successDialog: ModalDialog;
      confirmActionDialog: ModalDialog;
    }>(undefined);
    const apliKeyList = ref([]);
    const activityHeader = ref([
      {
        text: "Name",
        align: "left",
        sortable: false,
        value: "apiKeyName",
        class: "bold-header",
      },
      {
        text: "Environment",
        align: "left",
        sortable: false,
        value: "environment",
        class: "bold-header",
      },
      {
        text: "API Key",
        align: "left",
        sortable: false,
        value: "apiKey",
        class: "bold-header",
      },
      {
        text: "Actions",
        align: "right",
        sortable: false,
        value: "action",
        class: "bold-header",
      },
    ]);
    const initialize = async () => {
      await loadApiKeys();
    };
    const loadApiKeys = async () => {
      isLoading.value = true;
      apliKeyList.value = [];
      totalApiKeyCount.value = 0;
      try {
        const resp: any = await getOrgApiKeys(currentOrganization.id);
        apliKeyList.value = resp?.consumer?.consumerKey || [];
        totalApiKeyCount.value = resp?.consumer?.consumerKey.length || 0;
        isLoading.value = false;
      } catch (e) {
        isLoading.value = false;
      }
    };
    const confirmationModal = (apiKey) => {
      selectedApi.value = apiKey;
      const { apiKeyName } = apiKey;
      confirmActionTextLine1.value = `Revoking an API key will immediately disable and remove this API key.`;
      confirmActionTextLine2.value = `This action cannot be reversed. Are you sure you wish to remove <strong>${apiKeyName}</strong> API key?`;
      ctx.refs.confirmActionDialog.open();
    };
    const revokeApi = async () => {
      const orgId = currentOrganization.id;
      const { apiKey, apiKeyName } = selectedApi.value;
      const apiKeys = { orgId, apiKey };
      alertIcon.value = "mdi-alert-circle-outline";
      alertTitle.value = "API key has not been Revoked";
      alertText.value = `<strong>${apiKeyName}</strong> API Key has not been Revoked`;
      notificationColor.value = "error";
      isLoading.value = true;
      try {
        const resp: any = await revokeOrgApiKeys(apiKeys);
        if (resp) {
          alertIcon.value = "mdi-check";
          alertTitle.value = "API key has been Revoked";
          alertText.value = `<strong>${apiKeyName}</strong> API Key has been Revoked`;
          notificationColor.value = "success";
        }
      } catch (e) {
        console.log("error", e);
      }
      isLoading.value = false;
      await loadApiKeys();
      selectedApi.value = {};
      ctx.refs.confirmActionDialog.close();
      ctx.refs.successDialog.open();
    };
    const close = (dialog) => {
      dialog.close();
    };
    const getIndexedTag = (tag, idx) => {
      return `${tag}-${idx}`;
    };
    onMounted(async () => {
      setAccountChangedHandler(initialize);
      initialize();
    });
    return {
      isLoading,
      confirmActionTitle,
      confirmActionTextLine1,
      confirmActionTextLine2,
      alertText,
      alertTitle,
      alertIcon,
      notificationColor,
      totalApiKeyCount,
      selectedApi,
      $refs,
      apliKeyList,
      activityHeader,
      initialize,
      loadApiKeys,
      confirmationModal,
      revokeApi,
      close,
      getIndexedTag,
    };
  },
});
