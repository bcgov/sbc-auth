import { defineComponent, computed, ref } from "@vue/composition-api";
import { Component, Mixins, Prop, Vue, Watch } from "vue-property-decorator";
import { Member, MembershipType, Organization } from "@/models/Organization";
import {
  StatementListItem,
  StatementNotificationSettings,
  StatementRecipient,
  StatementSettings,
} from "@/models/statement";
import { mapActions, mapState } from "vuex";
import CommonUtils from "@/util/common-util";
import moment from "moment";
export default defineComponent({
  props: {},
  setup(_props, ctx) {
    const statementSettings = computed(
      () => ctx.root.$store.state.org.statementSettings
    );
    const currentStatementNotificationSettings = computed(
      () => ctx.root.$store.state.org.currentStatementNotificationSettings
    );
    const activeOrgMembers = computed(
      () => ctx.root.$store.state.org.activeOrgMembers
    );
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const fetchStatementSettings = () =>
      ctx.root.$store.dispatch("org/fetchStatementSettings");
    const getStatementRecipients = () =>
      ctx.root.$store.dispatch("org/getStatementRecipients");
    const updateStatementSettings = () =>
      ctx.root.$store.dispatch("org/updateStatementSettings");
    const syncActiveOrgMembers = () =>
      ctx.root.$store.dispatch("org/syncActiveOrgMembers");
    const updateStatementNotifications = () =>
      ctx.root.$store.dispatch("org/updateStatementNotifications");
    const fetchStatementSettings = ref<() => StatementSettings>(undefined);
    const getStatementRecipients =
      ref<() => StatementNotificationSettings>(undefined);
    const updateStatementSettings =
      ref<(statementFrequency: StatementListItem) => any>(undefined);
    const updateStatementNotifications =
      ref<(statementNotification: StatementNotificationSettings) => any>(
        undefined
      );
    const syncActiveOrgMembers = ref<() => Member[]>(undefined);
    const statementSettings = ref<StatementSettings>(undefined);
    const currentStatementNotificationSettings =
      ref<StatementNotificationSettings>(undefined);
    const currentOrganization = ref<Organization>(undefined);
    const activeOrgMembers = ref<Member[]>(undefined);
    const isSettingsModalOpen = ref<boolean>(false);
    const frequencySelected = ref<string>("");
    const sendStatementNotifications = ref<boolean>(false);
    const emailRecipientInput = ref<StatementRecipient>(
      {} as StatementRecipient
    );
    const emailRecipientList = ref<StatementRecipient[]>([]);
    const errorMessage = ref<string>("");
    const isFrequencyChanged = ref<boolean>(false);
    const isNotificationChanged = ref<boolean>(false);
    const isRecipientListChanged = ref<boolean>(false);
    const recipientAutoCompleteList = ref<StatementRecipient[]>([]);
    const isLoading = ref<boolean>(false);
    const isSaving = ref<boolean>(false);
    const showStatementNotification = ref<boolean>(false);
    const enableSaveBtn = computed(() => {
      return (
        isFrequencyChanged.value ||
        isNotificationChanged.value ||
        isRecipientListChanged.value
      );
    });
    const getIndexedTag = (tag, index): string => {
      return `${tag}-${index}`;
    };
    const openSettings = async () => {
      isLoading.value = true;
      try {
        errorMessage.value = "";
        isFrequencyChanged.value = false;
        isNotificationChanged.value = false;
        isRecipientListChanged.value = false;
        await syncActiveOrgMembers.value();
        const settings = await fetchStatementSettings.value();
        const statementRecipients = await getStatementRecipients.value();
        frequencySelected.value =
          settings?.currentFrequency?.frequency ||
          settings?.frequencies[0].frequency;
        sendStatementNotifications.value =
          statementRecipients.statementNotificationEnabled;
        emailRecipientList.value = [...statementRecipients.recipients];
        await prepareAutoCompleteList();
        isLoading.value = false;
        isSettingsModalOpen.value = true;
      } catch (error) {
        isLoading.value = false;
      }
    };
    const prepareAutoCompleteList = async () => {
      activeOrgMembers.value.forEach((member) => {
        const recipientIndex = emailRecipientList.value.findIndex(
          (emailRecipient) => emailRecipient.authUserId === member?.user?.id
        );
        if (
          recipientIndex < 0 &&
          member.membershipTypeCode !== MembershipType.User
        ) {
          recipientAutoCompleteList.value.push({
            authUserId: member.user?.id,
            firstname: member.user?.firstname,
            lastname: member.user?.lastname,
            name: `${member.user?.firstname || ""} ${
              member.user?.lastname || ""
            }`,
            email: member.user?.contacts[0]?.email,
          });
        }
      });
    };
    const closeSettings = () => {
      isSettingsModalOpen.value = false;
    };
    const updateSettings = async () => {
      errorMessage.value = "";
      try {
        isSaving.value = true;
        if (isFrequencyChanged.value) {
          await updateStatementSettings.value({
            frequency: frequencySelected.value,
          });
        }
        if (isNotificationChanged.value || isRecipientListChanged.value) {
          const recipientList = emailRecipientList.value.map((recipient) => {
            return {
              authUserId: recipient.authUserId,
              email: recipient.email,
              firstname: recipient.firstname,
              lastname: recipient.lastname,
            };
          });
          const statementNotification: StatementNotificationSettings = {
            statementNotificationEnabled: sendStatementNotifications.value,
            recipients: recipientList,
            accountName: currentOrganization.value.name,
          };
          await updateStatementNotifications.value(statementNotification);
        }
        showStatementNotification.value = true;
        isSaving.value = false;
        isSettingsModalOpen.value = false;
      } catch (error) {
        errorMessage.value = "Failed to update the settings, please try again.";
        isSaving.value = false;
      }
    };
    const frequencyChanged = (frequency) => {
      isFrequencyChanged.value =
        frequency !== statementSettings.value?.currentFrequency?.frequency;
    };
    const toggleStatementNotification = (notification) => {
      isNotificationChanged.value =
        notification !==
        currentStatementNotificationSettings.value.statementNotificationEnabled;
    };
    const setRecipientListChanged = () => {
      isRecipientListChanged.value =
        JSON.stringify(emailRecipientList.value) !==
        JSON.stringify(currentStatementNotificationSettings.value.recipients);
    };
    const formatDate = (value) => {
      return CommonUtils.formatDisplayDate(new Date(value));
    };
    const showFrequencyChangeDate = (frequency) => {
      return (
        frequency.frequency === frequencySelected.value &&
        frequency.frequency !==
          statementSettings.value?.currentFrequency?.frequency
      );
    };
    const capitalizeLabel = (value) => {
      return typeof value === "string"
        ? `${value.charAt(0)}${value.slice(1).toLowerCase()}`
        : "";
    };
    const addEmailReceipient = (item) => {
      if (item.authUserId) {
        emailRecipientList.value.push({ ...item });
        setRecipientListChanged();
        const recipientIndex = recipientAutoCompleteList.value.findIndex(
          (recipient) => recipient.authUserId === item.authUserId
        );
        if (recipientIndex > -1) {
          recipientAutoCompleteList.value.splice(recipientIndex, 1);
        }
        setTimeout(() => {
          emailRecipientInput.value = {} as StatementRecipient;
        }, 100);
      }
    };
    const removeEmailReceipient = (item) => {
      const index = emailRecipientList.value.indexOf(item);
      if (index > -1) {
        emailRecipientList.value.splice(index, 1);
      }
      setRecipientListChanged();
      item.name = `${item.firstname || ""} ${item.lastname || ""}`;
      recipientAutoCompleteList.value.push(item);
    };
    const selectFromListUsingKey = (itemIndex) => {
      if (itemIndex > -1) {
        addEmailReceipient(emailRecipientInput.value);
      }
    };
    return {
      statementSettings,
      currentStatementNotificationSettings,
      activeOrgMembers,
      currentOrganization,
      fetchStatementSettings,
      getStatementRecipients,
      updateStatementSettings,
      syncActiveOrgMembers,
      updateStatementNotifications,
      fetchStatementSettings,
      getStatementRecipients,
      updateStatementSettings,
      updateStatementNotifications,
      syncActiveOrgMembers,
      statementSettings,
      currentStatementNotificationSettings,
      currentOrganization,
      activeOrgMembers,
      isSettingsModalOpen,
      frequencySelected,
      sendStatementNotifications,
      emailRecipientInput,
      emailRecipientList,
      errorMessage,
      isFrequencyChanged,
      isNotificationChanged,
      isRecipientListChanged,
      recipientAutoCompleteList,
      isLoading,
      isSaving,
      showStatementNotification,
      enableSaveBtn,
      getIndexedTag,
      openSettings,
      prepareAutoCompleteList,
      closeSettings,
      updateSettings,
      frequencyChanged,
      toggleStatementNotification,
      setRecipientListChanged,
      formatDate,
      showFrequencyChangeDate,
      capitalizeLabel,
      addEmailReceipient,
      removeEmailReceipient,
      selectFromListUsingKey,
    };
  },
});
